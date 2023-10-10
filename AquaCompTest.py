from AquaComp import *


def test_loadaquareport():
    ar_file1 = './TestAR/AquaReport1.xml'
    return load_aquareport(ar_file1)


def test_compareaquareports():
    ar_file1 = './TestAR/AquaReport1.xml'
    ar_file2 = './TestAR/AquaReport2.xml'
    compare_aquareports(ar_file1, ar_file2, outfile='ar_comp.csv', diff_only=False)
    compare_aquareports(ar_file1, ar_file2, outfile='ar_comp_diff.csv', diff_only=True, compact=True)
    compare_aquareports(ar_file1, ar_file2, outfile='ar_comp_one.csv', diff_only=False, compact=True, one_line=True)
    compare_aquareports(ar_file1, ar_file2, outfile='ar_comp_one_diff.csv', diff_only=True, compact=True, one_line=True)


def test_compareprojectinfo():
    arx1, arx2 = load_aquareport('./TestAR/AquaReport1.xml'), load_aquareport('./TestAR/AquaReport2.xml')
    pi1, pi2 = get_projectinfo(arx1), get_projectinfo(arx2)
    diff1 = compare_projectinfo(pi1, pi2)
    diff2 = compare_projectinfo(pi1, pi2, diff_only=True)
    return diff1, diff2


def test_comparestagescore():
    arx1, arx2 = load_aquareport('./TestAR/AquaReport1.xml'), load_aquareport('./TestAR/AquaReport2.xml')
    score1, score2 = get_stagescore(arx1), get_stagescore(arx2)
    diff1 = compare_stagescore(score1, score2)
    diff2 = compare_stagescore(score1, score2, diff_only=True)
    return diff1, diff2


def test_comparefluxes():
    arx1, arx2 = load_aquareport('./TestAR/AquaReport1.xml'), load_aquareport('./TestAR/AquaReport2.xml')
    flux1, flux2 = get_flux(arx1), get_flux(arx2)
    diff1 = compare_fluxes(flux1, flux2)
    diff2 = compare_fluxes(flux1, flux2, diff_only=True, limit=1E-8)
    return diff1, diff2


def test_comparesensitivities():
    arx1, arx2 = load_aquareport('./TestAR/AquaReport1.xml'), load_aquareport('./TestAR/AquaReport2.xml')
    sens1, sens2 = get_sensitivity(arx1), get_sensitivity(arx2)
    diff1 = compare_sensitivities(sens1, sens2)
    diff2 = compare_sensitivities(sens1, sens2, diff_only=True, limit=1E-2)
    return diff1, diff2


def test_getcfmetrics():
    arx1 = load_aquareport('./TestAR/AquaReport1.xml')
    cf = get_cfmetrics(arx1)
    return cf


def test_comparecfmetrics():
    arx1, arx2 = load_aquareport('./TestAR/AquaReport1.xml'), load_aquareport('./TestAR/AquaReport2.xml')
    cf1, cf2 = get_cfmetrics(arx1), get_cfmetrics(arx2)
    diff = compare_cfmetrics(cf1, cf2, diff_only=False, limit=1E-2)
    return diff


if __name__ == '__main__':
    test_comparecfmetrics()
