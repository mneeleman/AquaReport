import xml.etree.ElementTree as ElT
import csv


def compare_aquareports(file1, file2, outfile='compare_aq.csv', stagecomplist=None):
    arx1 = load_aquareport(file1)
    arx2 = load_aquareport(file2)
    # the project information
    pi1 = get_projectinfo(arx1)
    pi2 = get_projectinfo(arx2)
    columns, row1, row2 = compare_projectinfo(pi1, pi2)
    with open(outfile, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns)
        csvwriter.writerow(row1)
        csvwriter.writerow(row2)
        csvwriter.writerow('')
    # qa scores per stage
    score1 = get_stagescore(arx1)
    score2 = get_stagescore(arx2)
    columns, row1 = compare_stagescore(score1, score2, stagecomplist=stagecomplist)
    with open(outfile, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['QA scores for the different PL stages'])
        csvwriter.writerow([key + ':' + score1[key]['Name'] for key in score1])
        csvwriter.writerow([score1[key]['Score'] for key in score1])
        csvwriter.writerow([key + ':' + score2[key]['Name'] for key in score2])
        csvwriter.writerow([score2[key]['Score'] for key in score2])
        csvwriter.writerow(columns)
        csvwriter.writerow(row1)
        csvwriter.writerow('')
    # flux measurements
    flux1 = get_flux(arx1)
    flux2 = get_flux(arx2)
    columns, row1 = compare_fluxes(flux1, flux2)
    with open(outfile, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Flux measurements for the calibrators per EB'])
        csvwriter.writerow([key for key in flux1])
        csvwriter.writerow([(flux1[key]['flux2'] if flux1[key]['flux2'] != 'None' else flux1[key]['flux1'])
                            for key in flux1])
        csvwriter.writerow([key for key in flux2])
        csvwriter.writerow([(flux2[key]['flux2'] if flux2[key]['flux2'] != 'None' else flux2[key]['flux1'])
                            for key in flux2])
        csvwriter.writerow(columns)
        csvwriter.writerow(row1)
        csvwriter.writerow('')
    # max renorm factors
    mrf1 = get_maxrenormfactor(arx1)
    mrf2 = get_maxrenormfactor(arx2)
    columns, row1 = compare_maxrenormfactor(mrf1, mrf2)
    with open(outfile, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Max renorm factors per EB and SPW'])
        csvwriter.writerow([key for key in mrf1])
        csvwriter.writerow([mrf1[key] for key in mrf1])
        csvwriter.writerow([key for key in mrf2])
        csvwriter.writerow([mrf2[key] for key in mrf2])
        csvwriter.writerow(columns)
        csvwriter.writerow(row1)
        csvwriter.writerow('')
    # image sensitivities
    sens1 = get_sensitivity(arx1)
    sens2 = get_sensitivity(arx2)
    s1col, s1row = [], []
    for key1 in sens1:
        for key2 in sens1[key1]:
            for key3 in sens1[key1][key2]:
                name = key1 + ':' + key2 + ':' + key3
                s1col.append(name)
                s1row.append(sens1[key1][key2][key3])
    s2col, s2row = [], []
    for key1 in sens2:
        for key2 in sens2[key1]:
            for key3 in sens2[key1][key2]:
                name = key1 + ':' + key2 + ':' + key3
                s2col.append(name)
                s2row.append(sens2[key1][key2][key3])
    columns, row1 = compare_sensitivities(sens1, sens2)
    with open(outfile, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Imaging characteristics'])
        csvwriter.writerow(s1col)
        csvwriter.writerow(s1row)
        csvwriter.writerow(s2col)
        csvwriter.writerow(s2row)
        csvwriter.writerow(columns)
        csvwriter.writerow(row1)
        csvwriter.writerow('')
        csvwriter.writerow('')


def compare_aquareport_line(file1, file2, to_array=False, outfile='diff.csv', outfile_id='a', stagecomplist=None,
                            diff_only=False, limit=1E-3):
    arx1 = load_aquareport(file1)
    arx2 = load_aquareport(file2)
    row1 = ['ProposalCode']
    row2 = [arx1.find('ProjectStructure').find('ProposalCode').text]
    # get stage diff
    score1 = get_stagescore(arx1)
    score2 = get_stagescore(arx2)
    trow1, trow2 = compare_stagescore(score1, score2, stagecomplist=stagecomplist)
    if diff_only:
        trow1, trow2 = __compare_diff__(trow1, trow2, limit=limit)
    row1.extend(trow1)
    row2.extend(trow2)
    # get flux diff
    flux1 = get_flux(arx1)
    flux2 = get_flux(arx2)
    trow1, trow2 = compare_fluxes(flux1, flux2)
    if diff_only:
        trow1, trow2 = __compare_diff__(trow1, trow2, limit=1E-3)
    row1.extend(trow1)
    row2.extend(trow2)
    # get renorm diff
    mrf1 = get_maxrenormfactor(arx1)
    mrf2 = get_maxrenormfactor(arx2)
    trow1, trow2 = compare_maxrenormfactor(mrf1, mrf2)
    if diff_only:
        trow1, trow2 = __compare_diff__(trow1, trow2, limit=1E-3)
    row1.extend(trow1)
    row2.extend(trow2)
    # get sens diff
    sens1 = get_sensitivity(arx1)
    sens2 = get_sensitivity(arx2)
    trow1, trow2 = compare_sensitivities(sens1, sens2)
    if diff_only:
        trow1, trow2 = __compare_diff__(trow1, trow2, limit=1E-3)
    row1.extend(trow1)
    row2.extend(trow2)
    if to_array:
        return row1, row2
    else:
        with open(outfile, outfile_id, newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row1)
            csvwriter.writerow(row2)


def get_projectinfo(arx):
    ps = arx.find('ProjectStructure')
    projectinfo = {}
    for x in list(ps):
        projectinfo[x.tag] = x.text
    qs = arx.find('QaSummary')
    for x in list(qs):
        projectinfo[x.tag] = x.text
    return projectinfo


def compare_projectinfo(pi1, pi2, to_array=True):
    keys = list(pi1.keys() | pi2.keys())
    diff = {'': {'ar1': 'AR1', 'ar2': 'AR2'}}
    for key in keys:
        diff[key] = {'ar1': '---', 'ar2': '---'}
        if key in pi1:
            diff[key]['ar1'] = pi1[key]
        if key in pi2:
            diff[key]['ar2'] = pi2[key]
    if to_array:
        columns = [x for x in diff]
        row1 = [diff[x]['ar1'] for x in diff]
        row2 = [diff[x]['ar2'] for x in diff]
        return columns, row1, row2
    else:
        return diff


def get_stagescore(arx):
    stagescore = {}
    for stage in arx.find('QaPerStage'):
        rep_score = stage.find('RepresentativeScore').attrib['Score']
        stagescore[stage.attrib['Number']] = {'Name': stage.attrib['Name'], 'Score': rep_score}
    return stagescore


def compare_stagescore(score1, score2, to_array=True, stagecomplist=None):
    if stagecomplist is None:
        stagecomplist = _get_stagecomplist_(score1, score2)
    diff = {}
    for stagecomp in stagecomplist:
        diff[stagecomp[0]] = {'Number': '{},{}'.format(stagecomp[0], stagecomp[1]),
                              'Name': score1[stagecomp[0]]['Name'],
                              'Value': __calc_diff__(score1[stagecomp[0]]['Score'], score2[stagecomp[1]]['Score'])}
    if to_array:
        row1 = ['QaStages:' + diff[x]['Number'] + ':' + diff[x]['Name'] for x in diff]
        row2 = [diff[x]['Value'] for x in diff]
        return row1, row2
    else:
        return diff


def get_flux(arx):
    flux = {}
    for fm in arx.iter('FluxMeasurement'):
        name = 'FluxMeasurment:' + fm.attrib['Asdm'] + ':' + fm.attrib['Field'] + ':' + fm.attrib['MsSpwId']
        if name not in flux:
            flux[name] = {'flux1': fm.attrib['FluxJy'], 'flux2': 'None'}
        else:
            flux[name]['flux2'] = fm.attrib['FluxJy']
    return flux


def compare_fluxes(flux1, flux2, to_array=True):
    diff = {}
    for key1 in flux1.keys():
        if key1 in flux2.keys():
            diff[key1] = {}
            fl1 = flux1[key1]['flux2'] if flux1[key1]['flux2'] != 'None' else flux1[key1]['flux1']
            fl2 = flux2[key1]['flux2'] if flux2[key1]['flux2'] != 'None' else flux2[key1]['flux1']
            diff[key1] = __calc_diff__(fl1, fl2)
    if to_array:
        row1 = [x for x in diff]
        row2 = [diff[x] for x in diff]
        return row1, row2
    else:
        return diff


def get_sensitivity(arx):
    sensdict = {}
    for sens in arx.iter('Sensitivity'):
        __populate_sensdict__(sensdict, sens.attrib)
    return sensdict


def compare_sensitivities(sens1, sens2, to_array=True):
    diff = {}
    for key1 in sens1.keys():
        if key1 in sens2.keys():
            diff[key1] = {}
            for key2 in sens1[key1].keys():
                if key2 in sens2[key1].keys():
                    diff[key1][key2] = __diff_sensitivities__(sens1[key1][key2], sens2[key1][key2])
    if to_array:
        row1, row2 = [], []
        for k1 in diff:
            for k2 in diff[k1]:
                for k3 in diff[k1][k2]:
                    row1.append('Sensitivity:' + k1 + ':' + k2 + ':' + k3)
                    row2.append(diff[k1][k2][k3])
        return row1, row2
    else:
        return diff


def get_maxrenormfactor(arx):
    mrf = {}
    for stage in arx.find('QaPerStage'):
        if stage.attrib['Name'] == 'hifa_renorm':
            for subscore in stage.findall('SubScore'):
                ebspw = ('MaxRenormFactor: ' + subscore.attrib['Reason'].split(' ')[1] + ': spw' +
                         subscore.attrib['Reason'].split(' ')[5][:-1])
                mrf[ebspw] = subscore.find('Metric').attrib['Value']
    return mrf


def compare_maxrenormfactor(mrf1, mrf2, to_array=True):
    diff = {}
    for key1 in mrf1.keys():
        if key1 in mrf2.keys():
            diff[key1] = __calc_diff__(mrf1[key1], mrf2[key1])
    if to_array:
        row1 = [x for x in diff]
        row2 = [diff[x] for x in diff]
        return row1, row2
    else:
        return diff


def load_aquareport(file_name):
    with open(file_name) as file:
        return ElT.parse(file).getroot()


def _get_stagecomplist_(score1, score2):
    stagelistshort = score1 if len(score1) < len(score2) else score2
    cnt1, cnt2 = 1, 1
    stagecomplist = []
    for stage in stagelistshort:
        tcnt1 = cnt1
        while score1[str(cnt1)]['Name'] != stagelistshort[stage]['Name']:
            cnt1 += 1
            if str(cnt1) not in score1:
                sc1 = 'None'
                cnt1 = tcnt1
                break
        else:
            sc1 = str(cnt1)
            cnt1 += 1
        tcnt2 = cnt2
        while score2[str(cnt2)]['Name'] != stagelistshort[stage]['Name']:
            cnt2 += 1
            if str(cnt2) not in score2:
                sc2 = 'None'
                cnt2 = tcnt2
                break
        else:
            sc2 = str(cnt2)
            cnt2 += 1
        if sc1 != 'None' and sc2 != 'None':
            stagecomplist.append((sc1, sc2))
    return stagecomplist


def __populate_sensdict__(sensdict, attrib):
    spwdict = {'Rms': attrib.get('SensitivityJyPerBeam', 'None'),
               'Bmaj': attrib.get('BeamMajArcsec', 'None'),
               'Bmin': attrib.get('BeamMinArcsec', 'None'),
               'Bpa': attrib.get('BeamPosAngDeg', 'None'),
               'Max': attrib.get('PbcorImageMaxJyPerBeam', 'None'),
               'Min': attrib.get('PbcorImageMinJyPerBeam', 'none')}
    if attrib['EffectiveBandwidthHz'] == 'N/A':
        return
    if 'DataType' not in attrib:
        data_type = 'REGCAL'
    else:
        data_type = attrib['DataType'].split('_')[0]
    sens_name = attrib['Field'] + ':' + attrib['Intent'] + ':' + data_type
    if sens_name not in sensdict:
        sensdict[sens_name] = {}
    if (attrib['MsSpwId'] + ':' + attrib['BwMode']) not in sensdict[sens_name]:
        sensdict[sens_name][(attrib['MsSpwId'] + ':' + attrib['BwMode'])] = spwdict


def __diff_sensitivities__(spwdict1, spwdict2):
    diffdict = {'Rms': __calc_diff__(spwdict1['Rms'], spwdict2['Rms']),
                'Bmaj': __calc_diff__(spwdict1['Bmaj'], spwdict2['Bmaj']),
                'Bmin': __calc_diff__(spwdict1['Bmin'], spwdict2['Bmin']),
                'Bpa': __calc_diff__(spwdict1['Bpa'], spwdict2['Bpa']),
                'Max': __calc_diff__(spwdict1['Max'], spwdict2['Max']),
                'Min': __calc_diff__(spwdict1['Min'], spwdict2['Min'])
                }
    return diffdict


def __calc_diff__(str1, str2):
    try:
        diff = str((float(str1) - float(str2)) / float(str1))
    except ZeroDivisionError:
        diff = str(-1 * float(str2))
    except ValueError:
        diff = 'None'
    return diff


def get_theoretical_rms(arx, stage_number):
    theoretical_rms = -1
    for stage in arx.find('QaPerStage'):
        if stage.attrib['Number'] == str(stage_number):
            for sub_score in stage.iter('SubScore'):
                if 'RMS vs. DR corrected sensitivity' in sub_score.attrib['Reason']:
                    theoretical_rms = eval(sub_score.find('Metric').attrib.get('Value'))[1]
                    break
    return theoretical_rms


def get_representative_score(arx, stage_number):
    representative_score = 0.
    for stage in arx.find('QaPerStage'):
        if stage.attrib['Number'] == str(stage_number):
            representative_score = stage.find('RepresentativeScore').attrib['Score']
            break
    return representative_score


def __compare_diff__(lst1, lst2, limit=1E-3):
    nlst1, nlst2 = [], []
    for x, y in zip(lst1, lst2):
        try:
            if abs(float(y)) > limit:
                nlst2.append(float(y))
                nlst1.append(x)
        except ValueError:
            continue
    return nlst1, nlst2
