import xml.etree.ElementTree as ElT
import csv
import numpy as np


def compare_aquareports(file1, file2, outfile='compare_aq.csv', stagecomplist=None, diff_only=False,
                        limits=None, one_line=False, compact=False, return_dict=False):
    # define the limits that are to be used
    if limits is None:
        limits = [1E-3, 1E-2, 1E-2, 1E-2]
    # load the dictionaries
    arx1, arx2 = load_aquareport(file1), load_aquareport(file2)
    pi1, pi2 = get_projectinfo(arx1), get_projectinfo(arx2)
    score1, score2 = get_stagescore(arx1), get_stagescore(arx2)
    flux1, flux2 = get_flux(arx1), get_flux(arx2)
    mrf1, mrf2 = get_maxrenormfactor(arx1), get_maxrenormfactor(arx2)
    sens1, sens2 = get_sensitivity(arx1), get_sensitivity(arx2)
    # compare the dictionaries
    pidiff = compare_projectinfo(pi1, pi2, diff_only=diff_only)
    scorediff = compare_stagescore(score1, score2, stagecomplist=stagecomplist, diff_only=diff_only, limit=limits[0])
    fluxdiff = compare_fluxes(flux1, flux2, diff_only=diff_only, limit=limits[1])
    mrfdiff = compare_maxrenormfactor(mrf1, mrf2, diff_only=diff_only, limit=limits[2])
    sensdiff = compare_sensitivities(sens1, sens2, diff_only=diff_only, limit=limits[3])
    # write out to csv
    if return_dict:
        return {**pidiff, **scorediff, **fluxdiff, **mrfdiff, **sensdiff}
    if not compact:
        conv2csv(pidiff, csvfile=outfile, comment=None, one_line=False)
        conv2csv(scorediff, csvfile=outfile, comment='QA scores for the different PL stages', one_line=one_line)
        conv2csv(fluxdiff, csvfile=outfile, comment='Flux measurements for the calibrators per EB', one_line=one_line)
        conv2csv(mrfdiff, csvfile=outfile, comment='Max renorm factors per EB and SPW', one_line=one_line)
        conv2csv(sensdiff, csvfile=outfile, comment='Imaging characteristics', one_line=one_line)
    else:
        diff = {**pidiff, **scorediff, **fluxdiff, **mrfdiff, **sensdiff}
        conv2csv(diff, csvfile=outfile, comment=None, one_line=one_line)


def compare_cf(file1, file2, outfile='compare_cf.csv', diff_only=False, limit=1E-2, one_line=False, return_dict=False,
               no_ebw=False):
    arx1, arx2 = load_aquareport(file1), load_aquareport(file2)
    cf1, cf2 = get_cfmetrics(arx1), get_cfmetrics(arx2)
    diff = compare_cfmetrics(cf1, cf2, diff_only=diff_only, limit=limit, no_ebw=no_ebw)
    if return_dict:
        return diff
    conv2csv(diff, csvfile=outfile, comment=None, one_line=one_line)


def get_projectinfo(arx):
    ps = arx.find('ProjectStructure')
    projectinfo = {}
    for x in list(ps):
        projectinfo[x.tag] = x.text
    qs = arx.find('QaSummary')
    for x in list(qs):
        projectinfo[x.tag] = x.text
    return projectinfo


def compare_projectinfo(pi1, pi2, diff_only=False):
    keys = list(pi1.keys() | pi2.keys())
    diff = {}
    for name in keys:
        diff[name] = {'ar1': '---', 'ar2': '---', 'diff': ''}
        if name in pi1:
            diff[name]['ar1'] = pi1[name]
        if name in pi2:
            diff[name]['ar2'] = pi2[name]
        if diff[name]['ar1'] != diff[name]['ar2']:
            diff[name]['diff'] = diff[name]['ar1'] + ' -- ' + diff[name]['ar2']
        else:
            diff[name]['diff'] = diff[name]['ar1']
        if diff_only and diff[name]['ar1'] == diff[name]['ar2']:
            del (diff[name])
    return diff


def get_stagescore(arx):
    stagescore = {}
    for stage in arx.find('QaPerStage'):
        rep_score = stage.find('RepresentativeScore').attrib['Score']
        stagescore[stage.attrib['Number']] = {'Name': stage.attrib['Name'], 'Score': rep_score}
    return stagescore


def compare_stagescore(score1, score2, stagecomplist=None, diff_only=False, limit=1E-3):
    if stagecomplist is None:
        stagecomplist = _get_stagecomplist_(score1, score2)
    diff = {}
    for stagecomp in stagecomplist:
        name = 'QaStages:{},{}:'.format(stagecomp[0], stagecomp[1]) + score1[stagecomp[0]]['Name']
        diff[name] = {'ar1stage': stagecomp[0] + ':' + score1[stagecomp[0]]['Name'],
                      'ar1': score1[stagecomp[0]]['Score'],
                      'ar2stage': stagecomp[1] + ':' + score2[stagecomp[1]]['Name'],
                      'ar2': score2[stagecomp[1]]['Score'],
                      'number': '{},{}'.format(stagecomp[0], stagecomp[1]),
                      'diff': __calc_diff__(score1[stagecomp[0]]['Score'], score2[stagecomp[1]]['Score'])}
        if diff_only:
            if diff[name]['diff'] == 'None':
                del (diff[name])
            else:
                if abs(float(diff[name]['diff'])) < limit:
                    del (diff[name])
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


def compare_fluxes(flux1, flux2, diff_only=False, limit=1E-2):
    diff = {}
    for name in flux1.keys():
        if name in flux2.keys():
            diff[name] = {}
            fl1 = flux1[name]['flux2'] if flux1[name]['flux2'] != 'None' else flux1[name]['flux1']
            fl2 = flux2[name]['flux2'] if flux2[name]['flux2'] != 'None' else flux2[name]['flux1']
            diff[name] = {'ar1': fl1, 'ar2': fl2, 'diff': __calc_percdiff__(fl1, fl2)}
            if diff_only:
                if diff[name]['diff'] == 'None':
                    del (diff[name])
                else:
                    if abs(float(diff[name]['diff'])) < limit:
                        del (diff[name])
    return diff


def get_sensitivity(arx, get_bw=False):
    sensdict = {}
    for sens in arx.iter('Sensitivity'):
        __populate_sensdict__(sensdict, sens.attrib, get_bw=get_bw)
    return sensdict


def compare_sensitivities(sens1, sens2, diff_only=False, limit=1E-2):
    diff = {}
    for key1 in sens1.keys():
        for key2 in sens1[key1].keys():
            for key3 in sens1[key1][key2]:
                name = 'Sensitivity:' + key1 + ':' + key2 + ':' + key3
                diff[name] = {'ar1': sens1[key1][key2][key3], 'ar2': sens2[key1][key2][key3],
                              'diff': __calc_percdiff__(sens1[key1][key2][key3], sens2[key1][key2][key3])}
                if diff_only:
                    if diff[name]['diff'] == 'None':
                        del (diff[name])
                    else:
                        if abs(float(diff[name]['diff'])) < limit:
                            del (diff[name])
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


def compare_maxrenormfactor(mrf1, mrf2, diff_only=True, limit=1E-2):
    diff = {}
    for name in mrf1.keys():
        if name in mrf2.keys():
            diff[name] = {'ar1': mrf1[name], 'ar2': mrf1[name], 'diff': __calc_percdiff__(mrf1[name], mrf2[name])}
            if diff_only:
                if diff[name]['diff'] == 'None':
                    del (diff[name])
                else:
                    if diff_only and abs(float(diff[name]['diff'])) < limit:
                        del (diff[name])
    return diff


def get_cfmetrics(arx, limit=25):
    sens = get_sensitivity(arx, get_bw=True)
    cf = {}
    for key1 in sens.keys():
        for key2 in sens[key1].keys():
            name = key1 + ':' + key2 + ':'
            s = sens[key1][key2]
            cf[name + 'effectivebw'] = str(float(s['Ebw'])/1E9)
            cf[name + 'rmsadj'] = str(float(s['Rms']) * np.sqrt(float(s['Ebw'])/1E9))
            cf[name + 'beamarea'] = str(np.sqrt(float(s['Bmin']) * float(s['Bmin'])) * 2 * np.pi / (2 * np.log(2)))
            cf[name + 'max'] = s['Max'] if abs(float(s['Max']) / float(s['Rms'])) > limit else 'None'
            cf[name + 'min'] = s['Min'] if abs(float(s['Min']) / float(s['Rms'])) > limit else 'None'
            cf[name + 'snrmaxadj'] = (str(float(s['Max']) / float(cf[name + 'rmsadj']))
                                      if abs(float(s['Max']) / float(s['Rms'])) > limit else 'None')
            cf[name + 'snrminadj'] = (str(float(s['Min']) / float(cf[name + 'rmsadj']))
                                      if abs(float(s['Min']) / float(s['Rms'])) > limit else 'None')
    return cf


def compare_cfmetrics(cf1, cf2, diff_only=False, limit=1E-2, no_ebw=False):
    diff = {}
    for name in cf1.keys():
        if name in cf2.keys():
            diff[name] = {'ar1': cf1[name], 'ar2': cf2[name], 'diff': __calc_percdiff__(cf1[name], cf2[name])}
            if diff_only:
                if diff[name]['diff'] == 'None':
                    del (diff[name])
                else:
                    if diff_only and abs(float(diff[name]['diff'])) < limit:
                        del (diff[name])
            if 'effectivebw' in name and no_ebw:
                del (diff[name])
    return diff


def load_aquareport(file_name):
    with open(file_name) as file:
        return ElT.parse(file).getroot()


def conv2csv(diff, csvfile, comment=None, one_line=False):
    with open(csvfile, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if comment is not None:
            csvwriter.writerow([comment])
        csvwriter.writerow([name for name in diff])
        if not one_line:
            csvwriter.writerow([diff[name]['ar1'] for name in diff])
            csvwriter.writerow([diff[name]['ar2'] for name in diff])
        csvwriter.writerow([diff[name]['diff'] for name in diff])
        if not one_line:
            csvwriter.writerow([])


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


def __populate_sensdict__(sensdict, attrib, get_bw=False):
    spwdict = {'Rms': attrib.get('SensitivityJyPerBeam', 'None'),
               'Bmaj': attrib.get('BeamMajArcsec', 'None'),
               'Bmin': attrib.get('BeamMinArcsec', 'None'),
               'Bpa': attrib.get('BeamPosAngDeg', 'None'),
               'Max': attrib.get('PbcorImageMaxJyPerBeam', 'None'),
               'Min': attrib.get('PbcorImageMinJyPerBeam', 'None')}
    if get_bw:
        spwdict['Ebw'] = attrib.get('EffectiveBandwidthHz', 'None')

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


def __calc_diff__(str1, str2):
    try:
        diff = str((float(str2) - float(str1)))
    except ValueError:
        diff = 'None'
    return diff


def __calc_percdiff__(str1, str2):
    try:
        diff = str((float(str2) - float(str1)) / float(str1))
    except ZeroDivisionError:
        diff = str(float(str2))
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
