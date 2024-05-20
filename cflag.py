import xml.etree.ElementTree as ElT
import glob
import numpy as np
from astropy.io import fits
import os
import json


def cflag_output(pl_dir, proj_dir, to_jsonfile=False, jsonfile=None):
    strct = {'pipeline_dir': pl_dir, 'project_dir': proj_dir}
    __scrape_aquareport__(strct, pl_dir, proj_dir)
    __scrape_weblog__(strct, pl_dir, proj_dir)
    __get_targetlist__(strct, pl_dir, proj_dir)
    working_dir = __get_imagelist__(strct, pl_dir, proj_dir, return_workingdir=True)
    for image in strct['image_list']:
        print('cflag_output: working on {0}, {1:3.1f}%'.format(image, strct['image_list'].index(image) /
                                                               len(strct['image_list']) * 100))
        __get_imagestats__(strct, image, working_dir)
    if not to_jsonfile:
        return strct
    else:
        if jsonfile is None:
            jsonfile = strct['proposal_code'] + '_' + '_'.join(strct['mous_uid'].split('/')) + '.json'
        with open(jsonfile, 'w') as fp:
            json.dump(strct, fp)


def cflag_rundirectory(pl_dir, outdir='./', projects=None):
    if projects is None:
        projects = list(np.unique([x.split('/')[-2] for x in sorted(glob.glob(pl_dir + '/*.*/'))]))
    for proj_dir in projects:
        print('{0}: {1} of {2}'.format(proj_dir, projects.index(proj_dir) + 1, len(projects)))
        cflag_output(pl_dir, proj_dir, to_jsonfile=True, jsonfile=outdir + proj_dir + '.json')


def __scrape_aquareport__(strct, pl_dir, proj_dir):
    # check the product directoty for the aqua report
    arlist = glob.glob('{0}/{1}/S*/G*/M*/products/*.pipeline_aquareport.xml'.format(pl_dir, proj_dir))
    if not arlist:  # also check the working directory
        arlist = glob.glob('{0}/{1}/S*/G*/M*/working/pipeline_aquareport.xml'.format(pl_dir, proj_dir))
    if not arlist:
        print('__scrape_aquareport__: aquareport cannot be loaded for {0}/{1}'.format(pl_dir, proj_dir))
        strct['proposal_code'] = ''
        strct['project_uid'] = ''
        strct['mous_uid'] = ''
        strct['casa_version'] = ''
        strct['pipeline_version'] = ''
        strct['pipeline_recipe'] = ''
        strct['total_time'] = ''
    else:
        ar = ElT.parse(open(arlist[0], 'r')).getroot()
        strct['proposal_code'] = ar.find('ProjectStructure').find('ProposalCode').text
        strct['project_uid'] = ar.find('ProjectStructure').find('OusEntityId').text
        strct['mous_uid'] = ar.find('ProjectStructure').find('OusStatusEntityId').text
        strct['casa_version'] = ar.find('QaSummary').find('CasaVersion').text
        strct['pipeline_version'] = ar.find('QaSummary').find('PipelineVersion').text
        strct['pipeline_recipe'] = ar.find('ProjectStructure').find('ProcessingProcedure').text
        strct['total_time'] = ar.find('QaSummary').find('ProcessingTime').text


def __scrape_weblog__(strct, pl_dir, proj_dir):
    # look for weblog in the working directory (already untarred version)
    wllist = glob.glob('{0}/{1}/S*/G*/M*/working/pipeline_*/'.format(pl_dir, proj_dir))
    if not wllist:
        print('__scrape_weblog__: TODO look for tarred pipeline version in products directory')
    # take latest pipeline weblog
    pass


def __get_targetlist__(strct, pl_dir, proj_dir):
    imlist = glob.glob(pl_dir + '/' + proj_dir + '/S*/G*/M*/products/*_sci*')
    if not imlist:
        print('__get_targetlist__: no images in {0}/{1}'.format(pl_dir, proj_dir))
        strct['target_list'] = []
    else:
        target_list = list(np.unique([x.split('/')[-1].split('.')[1][:-4] for x in imlist]))
        strct['target_list'] = target_list


def __get_imagelist__(strct, pl_dir, proj_dir, return_workingdir=False):
    imlist = glob.glob(pl_dir + '/' + proj_dir + '/S*/G*/M*/products/*_sci*.pbcor.fits')
    if not imlist:
        print('__get_imagelist__: no images in {0}/{1}'.format(pl_dir, proj_dir))
        strct['image_list'] = []
        if return_workingdir:
            return ''
    else:
        image_list = [x.split('/')[-1] for x in imlist if 'tt1.pbcor.fits' not in x]
        strct['image_list'] = image_list
        if return_workingdir:
            return '/'.join(imlist[0].split('/')[:-1]) + '/'


def __get_imagestats__(strct, image, working_dir):
    header, im, im_pbcor, im_pb, im_mask = __load_images__(image, working_dir)
    header.remove('HISTORY', remove_all=True)
    string_header = header.tostring()
    im_rms, im_rmsidx, im_mad = __get_rms__(im, im_pb, im_mask)
    im_max, im_maxidx = __get_max__(im)
    rms_cutouts, rms_channels = __get_cutouts__(im, im_rmsidx)
    max_cutouts, max_channels = __get_cutouts__(im, im_maxidx)
    stat_strct = {'header': string_header, 'target': header['OBJECT'], 'spw': header['SPW'], 'type': header['FILNAM05'],
                  'rms': im_rms, 'rms_channels': rms_channels, 'rms_cutouts': rms_cutouts, 'mad': im_mad,
                  'im_rmsidx': im_rmsidx, 'max': im_max, 'max_channels': max_channels, 'max_cutouts': max_cutouts,
                  'im_maxidx': im_maxidx}
    strct[image] = stat_strct


def __get_rms__(im, im_pb, im_mask):
    if im.ndim == 2:
        pb_limit = __getpblimit__(im_pb)
        im_pbmaskcomp = np.where((~im_mask) & (im_pb < pb_limit), im, np.NaN)
        im_rms = [np.sqrt(np.nanmean(np.square(im_pbmaskcomp))).astype(np.float64)]
        im_mad = [np.nanmedian(np.abs(im_pbmaskcomp - np.nanmedian(im_pbmaskcomp))).astype(np.float64)]
        im_maskcomp = np.where((~im_mask) & (im_pb > pb_limit), 0, 1)
        im_rmsidx = list(np.random.randint(im_maskcomp.shape))
        while im_maskcomp[im_rmsidx[0], im_rmsidx[1]]:
            im_rmsidx = list(np.random.randint(im_maskcomp.shape))
        im_rmsidx = [im_rmsidx]
    else:
        if im.shape[-3] == 1:
            print('__get_rms__: only 1 channel --expect to break stuff')
        im_rms, temp_rmsidx, im_mad = [], [], []
        for channel in np.arange(im.shape[-3]):
            pb_limit = __getpblimit__(im_pb[channel, :])
            im_pbmaskcomp = np.where(~im_mask[channel, :] & (im_pb[channel, :] < pb_limit), im[channel, :], np.NaN)
            im_rms.append(np.sqrt(np.nanmean(np.square(im_pbmaskcomp))).astype(np.float64))
            im_mad.append(np.nanmedian(np.abs(im_pbmaskcomp - np.nanmedian(im_pbmaskcomp))).astype(np.float64))
            im_maskcomp = np.where((~im_mask[channel, :]) & (im_pb[channel, :] > pb_limit), 0, 1)
            t_rmsidx = np.random.randint(im_maskcomp.shape)
            while im_maskcomp[t_rmsidx[-2], t_rmsidx[-1]]:
                t_rmsidx = np.random.randint(im_maskcomp.shape)
            temp_rmsidx.append([channel, t_rmsidx[-2], t_rmsidx[-1]])
        maxidx, minidx = temp_rmsidx[np.nanargmax(im_rms)], temp_rmsidx[np.nanargmin(im_rms)]
        gradidx = temp_rmsidx[np.nanargmax(np.gradient(im_rms[:-1])) + 1]
        im_rmsidx = [minidx, maxidx, gradidx]
    return im_rms, im_rmsidx, im_mad


def __get_max__(im):
    if im.ndim == 2:
        im_max = [np.nanmax(im).astype(np.float64)]
        im_maxidx = [list(np.unravel_index(np.nanargmax(im), im.shape))]
    else:
        if im.shape[-3] == 1:
            print('__get_max__: only 1 channel --expect to break stuff')
        im_max, temp_maxidx = [], []
        for channel in np.arange(im.shape[-3]):
            im_max.append(np.nanmax(im[channel, :]).astype(np.float64))
            t_maxidx = np.unravel_index(np.nanargmax(im[channel, :]), im[channel, :].shape)
            temp_maxidx.append([channel, t_maxidx[-2], t_maxidx[-1]])
        maxidx, minidx = temp_maxidx[np.nanargmax(im_max)], temp_maxidx[np.nanargmin(im_max)]
        gradidx = temp_maxidx[np.nanargmax(np.gradient(im_max[:-1])) + 1]
        im_maxidx = [minidx, maxidx, gradidx]
    return im_max, im_maxidx


def __get_cutouts__(im, im_idx, sz=12):
    if im.ndim == 2:
        cutouts = []
        for i_idx in im_idx:
            cutouts.append(im[i_idx[-2] - sz:i_idx[-2] + sz + 1, i_idx[-1] - sz:i_idx[-1] + sz + 1].tolist())
        channels = [0]
    else:
        cutouts, channels = [], []
        for i_idx in im_idx:

            cutouts.append(im[i_idx[-3], i_idx[-2]-sz:i_idx[-2]+sz+1, i_idx[-1]-sz:i_idx[-1]+sz+1].tolist())
            channels.append(i_idx[-3].item())
    return cutouts, channels


def __load_images__(image, working_dir):
    hdu = fits.open(working_dir + image)
    header = hdu[0].header
    im_pbcor = np.squeeze(hdu[0].data)
    if '.tt0' in image:
        ext = '.tt0'
    else:
        ext = ''
    im_pb = np.squeeze(fits.open(working_dir + image.replace(ext + '.pbcor', '.pb' + ext))[0].data)
    if os.path.exists(working_dir + image.replace(ext + '.pbcor', 'mask')):
        im_mask = np.squeeze(fits.open(working_dir + image.replace(ext + '.pbcor', '.mask'))[0].data).astype(bool)
    else:
        im_mask = np.zeros_like(im_pbcor).astype(bool)
    im = im_pbcor * im_pb
    return header, im, im_pbcor, im_pb, im_mask


def __getpblimit__(im_pb):
    if np.min(im_pb) > 1.1 * 0.3:
        pb_limit = 1.1 * np.min(im_pb)
    else:
        pb_limit = 0.33
    return pb_limit
