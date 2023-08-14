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
<<<<<<< HEAD
        csvwriter.writerow(row1)
        csvwriter.writerow('')
    # flux measurements
    flux1 = get_flux(arx1)
    flux2 = get_flux(arx2)
    columns, row1 = compare_fluxes(flux1, flux2)
    with open(outfile, 'a', newline='') as csvfile:
=======
        csvwriter.writerow(c1text)
        csvwriter.writerow(c2text)


def compare_qastages(ar_file1, ar_file2, outfile='qa_stages.csv', outfile_id='w'):
    arx1, arx2 = load_aquareport(ar_file1), load_aquareport(ar_file2)
    el1, el2 = arx1.find('QaPerStage'), arx2.find('QaPerStage')
    # take the longer list as the one that defines the stage columns
    longer_list = list(el1) if len(list(el1)) > len(list(el2)) else list(el2)
    columns1 = [x.attrib['Name'] for x in longer_list]
    columns1.insert(0, 'StageName')
    columns2 = [x.attrib['Number'] for x in longer_list]
    columns2.insert(0, 'StageNumber')
    c1score, cnt1, c2score, cnt2 = ['AR1'], 0, ['AR2'], 0
    for col1 in columns1[1:]:
        try:
            if list(el1)[cnt1].attrib['Name'] == col1:
                c1score.append(list(el1)[cnt1].find('RepresentativeScore').attrib['Score'])
                cnt1 += 1
            else:
                c1score.append('None')
        except IndexError:
            c1score.append('None')
        try:
            if list(el2)[cnt2].attrib['Name'] == col1:
                c2score.append(list(el2)[cnt2].find('RepresentativeScore').attrib['Score'])
                cnt2 += 1
            else:
                c2score.append('None')
        except IndexError:
            c2score.append('None')
    with open(outfile, outfile_id, newline='') as csvfile:
>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0
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


<<<<<<< HEAD
def compare_aquareport_line(file1, file2, to_array=False, outfile='diff.csv', outfile_id='a', stagecomplist=None):
    arx1 = load_aquareport(file1)
    arx2 = load_aquareport(file2)
    row1 = ['ProposalCode']
    row2 = [arx1.find('ProjectStructure').find('ProposalCode').text]
    # get stage diff
    score1 = get_stagescore(arx1)
    score2 = get_stagescore(arx2)
    trow1, trow2 = compare_stagescore(score1, score2, stagecomplist=stagecomplist)
    row1.extend(trow1)
    row2.extend(trow2)
    # get flux diff
    flux1 = get_flux(arx1)
    flux2 = get_flux(arx2)
    trow1, trow2 = compare_fluxes(flux1, flux2)
    row1.extend(trow1)
    row2.extend(trow2)
    # get renorm diff
    mrf1 = get_maxrenormfactor(arx1)
    mrf2 = get_maxrenormfactor(arx2)
    trow1, trow2 = compare_maxrenormfactor(mrf1, mrf2)
    row1.extend(trow1)
    row2.extend(trow2)
    # get sens diff
    sens1 = get_sensitivity(arx1)
    sens2 = get_sensitivity(arx2)
    trow1, trow2 = compare_sensitivities(sens1, sens2)
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
=======
def compare_aquareports(ar_file1, ar_file2, outfile='compare_aq.csv'):
    compare_projectstructure(ar_file1, ar_file2, outfile=outfile, outfile_id='a')
    compare_qasummary(ar_file1, ar_file2, outfile=outfile, outfile_id='a')
    compare_qastages(ar_file1, ar_file2, outfile=outfile, outfile_id='a')
    compare_qatopic(ar_file1, ar_file2, outfile=outfile, outfile_id='a')


def _compare_xml_children_text_(xml1, xml2, element_name):
    el1, el2 = xml1.find(element_name), xml2.find(element_name)
    c1tag, c2tag = {x.tag for x in list(el1)}, {x.tag for x in list(el2)}
    columns = list(c1tag | c2tag)
    columns.insert(0, ' ')
    c1text, c2text = ['AR1'], ['AR2']
    for column in columns[1:]:
        try:
            c1text.append(el1.find(column).text)
        except AttributeError:
            c1text.append('None')
        try:
            c2text.append(el2.find(column).text)
        except AttributeError:
            c2text.append('None')
    return columns, c1text, c2text
>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0


def get_stagescore(arx):
    stagescore = {}
    for stage in arx.find('QaPerStage'):
        rep_score = stage.find('RepresentativeScore').attrib['Score']
        stagescore[stage.attrib['Number']] = {'Name': stage.attrib['Name'], 'Score': rep_score}
    return stagescore


<<<<<<< HEAD
def compare_stagescore(score1, score2, to_array=True, stagecomplist=None):
    if stagecomplist is None:
        stagecomplist = _get_stagecomplist_(score1, score2)
    diff = {}
    for stagecomp in stagecomplist:
        diff[stagecomp[0]] = {'Number': '{},{}'.format(stagecomp[0], stagecomp[1]),
                              'Name': score1[stagecomp[0]]['Name'],
                              'Value': __calc_diff__(score1[stagecomp[0]]['Score'], score2[stagecomp[1]]['Score'])}
=======
def compare_stagescore(score1, score2, to_array=True):
    rep_stages = score1 if len(score1) > len(score2) else score2
    stg_cnt1, stg_cnt2, diff = 1, 1, {}
    for stage_num in range(len(rep_stages)):
        name = rep_stages[str(stage_num + 1)]['Name']
        try:
            if score1[str(stg_cnt1)]['Name'] == name:
                sc1 = score1[str(stg_cnt1)]['Score']
                stg_cnt1 += 1
            else:
                sc1 = 'None'
        except KeyError:
            sc1 = 'None'
        try:
            if score2[str(stg_cnt2)]['Name'] == name:
                sc2 = score2[str(stg_cnt2)]['Score']
                stg_cnt2 += 1
            else:
                sc2 = 'None'
        except KeyError:
            sc2 = 'None'
        if sc1 != 'None' and sc2 != 'None':
            diff[stage_num] = {'Number': stage_num + 1, 'Name': name, 'Diff': __calc_diff__(sc1, sc2)}
        else:
            diff[stage_num] = {'Number': stage_num + 1, 'Name': name, 'Diff': __calc_diff__(sc1, sc2)}
>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0
    if to_array:
        row1 = ['QaStages:' + diff[x]['Number'] + ':' + diff[x]['Name'] for x in diff]
        row2 = [diff[x]['Value'] for x in diff]
        return row1, row2
    else:
        return diff


def get_flux(arx):
    flux = {}
    for fm in arx.iter('FluxMeasurement'):
<<<<<<< HEAD
        name = 'FluxMeasurment:' + fm.attrib['Asdm'] + ':' + fm.attrib['Field'] + ':' + fm.attrib['MsSpwId']
=======
        name = fm.attrib['Field'] + ':' + fm.attrib['MsSpwId'] + ':Flux'
>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0
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


<<<<<<< HEAD
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
=======
def compare_aquareport_line(file1, file2, outfile='diff.csv', to_array=False, outfile_id='a'):
    arx1 = load_aquareport(file1)
    arx2 = load_aquareport(file2)
    row1 = ['ProposalCode']
    row2 = [arx1.find('ProjectStructure').find('ProposalCode').text]
    # get stage diff
    score1 = get_stagescore(arx1)
    score2 = get_stagescore(arx2)
    trow1, trow2 = compare_stagescore(score1, score2)
    row1.extend(trow1)
    row2.extend(trow2)
    # get flux diff
    flux1 = get_flux(arx1)
    flux2 = get_flux(arx2)
    trow1, trow2 = compare_fluxes(flux1, flux2)
    row1.extend(trow1)
    row2.extend(trow2)
    # get sens diff
    sens1 = get_sensitivity(arx1)
    sens2 = get_sensitivity(arx2)
    trow1, trow2 = compare_sensitivities(sens1, sens2)
    row1.extend(trow1)
    row2.extend(trow2)
>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0
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
<<<<<<< HEAD
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
=======
               'Min': attrib.get('PbcorImageMinJyPerBeam', 'None')}
    if attrib['Field'] + ':' + attrib['Intent'] not in sensdict:
        sensdict[attrib['Field'] + ':' + attrib['Intent']] = {}
    if (attrib['MsSpwId'] + ':' + attrib['BwMode']) not in sensdict[attrib['Field'] + ':' + attrib['Intent']]:
        sensdict[attrib['Field'] + ':' + attrib['Intent']][(attrib['MsSpwId'] + ':' + attrib['BwMode'])] = spwdict
>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0


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
<<<<<<< HEAD
=======

>>>>>>> 938744e79a0eb27997a3f3f3aa3ec1880cd3cba0
