import xml.etree.ElementTree as ElT
import csv


def load_aquareport(file_name):
    with open(file_name) as file:
        return ElT.parse(file).getroot()


def compare_qaperstagevsqapertopic(ar_file):
    arx = load_aquareport(ar_file)
    el1 = arx.findall('QaPerStage')[0]
    el2 = arx.findall('QaPerTopic')[0]
    for c1 in el1:
        for d2 in el2.iter('Stage'):
            if d2.attrib['Number'] == c1.attrib['Number']:
                for d1, dd2 in zip(c1.iter(), d2.iter()):
                    print('True') if d1.attrib == dd2.attrib else print(d1.attrib, dd2.attrib)


def compare_projectstructure(ar_file1, ar_file2, outfile='project_structure.csv', outfile_id='w'):
    arx1, arx2 = load_aquareport(ar_file1), load_aquareport(ar_file2)
    columns, c1text, c2text = _compare_xml_children_text_(arx1, arx2, 'ProjectStructure')
    with open(outfile, outfile_id, newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns)
        csvwriter.writerow(c1text)
        csvwriter.writerow(c2text)


def compare_qasummary(ar_file1, ar_file2, outfile='qa_summary.csv', outfile_id='w'):
    arx1, arx2 = load_aquareport(ar_file1), load_aquareport(ar_file2)
    columns, c1text, c2text = _compare_xml_children_text_(arx1, arx2, 'QaSummary')
    with open(outfile, outfile_id, newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns)
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
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns1)
        csvwriter.writerow(columns2)
        csvwriter.writerow(c1score)
        csvwriter.writerow(c2score)


def compare_qatopic(ar_file1, ar_file2, flux_measurements=True, sensitivities=True,
                    outfile='qa_topic.csv', outfile_id='w'):
    ar1_xml, ar2_xml = load_aquareport(ar_file1), load_aquareport(ar_file2)
    el1, el2 = ar1_xml.find('QaPerTopic'), ar2_xml.find('QaPerTopic')
    with open(outfile, outfile_id, newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if flux_measurements:
            fm_col, fm_c1, fm_c2 = ['FluxMeasurements'], ['AR1'], ['AR2']
            fm_zip = zip(el1[0].find('FluxMeasurements').findall('FluxMeasurement'),
                         el2[0].find('FluxMeasurements').findall('FluxMeasurement'))
            for fm1, fm2 in fm_zip:
                fm_col.append(fm1.attrib['Field'] + ' for spw ' + fm1.attrib['MsSpwId'])
                fm_c1.append(fm1.attrib['FluxJy'] + ' Jy at ' + fm1.attrib['FrequencyGHz'] + ' GHz')
                fm_c2.append(fm2.attrib['FluxJy'] + ' Jy at ' + fm2.attrib['FrequencyGHz'] + ' GHz')
            fm_zip = zip(el1[2].find('FluxMeasurements').findall('FluxMeasurement'),
                         el2[2].find('FluxMeasurements').findall('FluxMeasurement'))
            for fm1, fm2 in fm_zip:
                fm_col.append(fm1.attrib['Field'] + ' in spw ' + fm1.attrib['MsSpwId'])
                fm_c1.append(fm1.attrib['FluxJy'] + ' Jy at ' + fm1.attrib['FrequencyGHz'] + ' GHz')
                fm_c2.append(fm2.attrib['FluxJy'] + ' Jy at ' + fm2.attrib['FrequencyGHz'] + ' GHz')
            csvwriter.writerow(fm_col)
            csvwriter.writerow(fm_c1)
            csvwriter.writerow(fm_c2)
        if sensitivities:
            se_col1, se_col2, se_c1, se_c2 = ['Sensitivities'], [''], ['AR1'], ['AR2']
            se_zip = zip(el1[0].find('SensitivityEstimates').findall('Sensitivity'),
                         el2[0].find('SensitivityEstimates').findall('Sensitivity'))
            for se1, se2 in se_zip:
                se_col1.append(se1.attrib['Field'] + ' for BWmode ' + se1.attrib['BwMode'])
                [se_col1.append('') for _x in range(3)]
                col_names = ['SensitivityJyPerBeam', 'BeamMajArcsec', 'BeamMinArcsec', 'BeamPosAngDeg']
                [se_col2.append(col_name) for col_name in col_names]
                [se_c1.append(se1.attrib[col_name]) for col_name in col_names]
                [se_c2.append(se2.attrib[col_name]) for col_name in col_names]
            csvwriter.writerow(se_col1)
            csvwriter.writerow(se_col2)
            csvwriter.writerow(se_c1)
            csvwriter.writerow(se_c2)


def compare_aquareports(ar_file1, ar_file2, outfile='compare_aq.csv'):
    compare_projectstructure(ar_file1, ar_file2, outfile=outfile, outfile_id='w')
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


def get_stagescore(arx):
    stagescore = {}
    for stage in arx.find('QaPerStage'):
        rep_score = stage.find('RepresentativeScore').attrib['Score']
        stagescore[stage.attrib['Number']] = {'Name': stage.attrib['Name'], 'Score': rep_score}
    return stagescore


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
    if to_array:
        row1 = [str(diff[x]['Number']) + ':' + diff[x]['Name'] for x in diff]
        row2 = [diff[x]['Diff'] for x in diff]
        return row1, row2
    else:
        return diff


def get_flux(arx):
    flux = {}
    for fm in arx.iter('FluxMeasurement'):
        name = fm.attrib['Field'] + ':' + fm.attrib['MsSpwId'] + ':Flux'
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
            if fl1 != 'None' and fl2 != 'None':
                diff[key1] = __calc_diff__(fl1, fl2)
            else:
                diff[key1] = 'None'
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
                    row1.append(k1+':'+k2+':'+k3)
                    row2.append(diff[k1][k2][k3])
        return row1, row2
    else:
        return diff


def compare_aquareport_line(file1, file2, to_array=False, outfile='diff.csv', to_array=False, outfile_id='a'):
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
    if to_array:
        return row1, row2
    else:
        with open(outfile, outfile_id, newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row1)
            csvwriter.writerow(row2)


def __populate_sensdict__(sensdict, attrib):
    spwdict = {'Rms': attrib.get('SensitivityJyPerBeam', 'None'),
               'Bmaj': attrib.get('BeamMajArcsec', 'None'),
               'Bmin': attrib.get('BeamMinArcsec', 'None'),
               'Bpa': attrib.get('BeamPosAngDeg', 'None'),
               'Max': attrib.get('PbcorImageMaxJyPerBeam', 'None'),
               'Min': attrib.get('PbcorImageMinJyPerBeam', 'None')}
    if attrib['Field'] + ':' + attrib['Intent'] not in sensdict:
        sensdict[attrib['Field'] + ':' + attrib['Intent']] = {}
    if (attrib['MsSpwId'] + ':' + attrib['BwMode']) not in sensdict[attrib['Field'] + ':' + attrib['Intent']]:
        sensdict[attrib['Field'] + ':' + attrib['Intent']][(attrib['MsSpwId'] + ':' + attrib['BwMode'])] = spwdict


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


def __get_attrib_not_used__(subs):
    reason_split = subs.attrib['Reason'].split()
    try:
        field = reason_split[reason_split.index('Field:') + 1]
        intent = reason_split[reason_split.index('Intent:') + 1]
    except ValueError:
        field, intent = 'None', 'None'
    rms = subs.find('Metric').get('Value')[0]
    attrib = {'Field': field, 'Intent': intent, 'SensitivityJyPerBeam': rms}
    return attrib


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

