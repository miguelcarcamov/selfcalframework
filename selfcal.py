import numpy as np
from flagmanager import flagmanager
from rmtables import rmtables
from gaincal import gaincal
from plotcal import plotcal
from applycal import applycal
from split import split


class Selfcal(object):

    def __init__(self, visfile="", imagename="", minblperant=0, refant="", spwmap=[], Imager=None, want_plot=False):
        self.visfile = visfile
        self.imagename = imagename
        self.minblperant = minblperant
        self.refant = refant
        self.spwmap = spwmap
        self.Imager = Imager
        self.want_plot = want_plot

    def plot_selfcal(self, caltable, xaxis="", yaxis="", timerange="", iteration="", antenna="", subplot=111, plotrange=[], want_plot=False):
        if want_plot:
            plotcal(caltable=caltable, xaxis=xaxis, yaxis=yaxis, timerange=timerange,
                    iteration=iteration, subplot=subplot, antenna=antenna, plotrange=plotrange)

    def selfcal_output(self):
        split(vis=self.visfile, outputvis=self.visfile +
              '.selfcal', datacolumn='corrected')


class Ampcal(Selfcal):
    def __init__(self, selfcal_object, minsnr=1.0, solint=[], combine="", input_caltable=""):
        super(Ampcal, self).__init__(selfcal_object.visfile, selfcal_object.imagename, selfcal_object.minblperant,
                                     selfcal_object.refant, selfcal_object.spwmap, selfcal_object.Imager, selfcal_object.want_plot)
        self.calmode = 'a'
        self.minsnr = minsnr
        self.solint = solint
        self.combine = combine
        self.input_caltable = input_caltable
        self.loops = len(self.solint)

    def run(self):
        caltable = ""
        for i in range(0, self.loops):
            caltable = 'ampcal_' + str(i)
            rmtables(caltable)
            gaincal(vis=self.visfile, field=self.Imager.getField(), caltable=caltable, spw=self.Imager.getSpw(), gaintype='G', refant=self.refant, calmode=self.calmode,
                    combine=self.combine, solint=self.solint[i], minsnr=self.minsnr, minblperant=self.minblperant, gaintable=self.input_caltable, spwmap=self.spwmap, solnorm=True)

            self.plot_selfcal(caltable, xaxis="time", yaxis="amp", iteration="antenna", subplot=421, plotrange=[0, 0, 0.2, 1.8], self.want_plot)

            applycal(vis=self.visfile, spwmap=[self.spwmap, self.spwmap], field=self.Imager.getField(), gaintable=[
                     self.input_caltable, caltable], gainfield='', calwt=False, flagbackup=False, interp='linearperobs')

            flagmanager(vis=self.visfile, mode='save',
                        versionname='after_ampcal' + str(i))

            imagename = self.imagename + '_a' + str(i)

            self.Imager.run(imagename)
        return caltable


class Phasecal(Selfcal):
    def __init__(self, selfcal_object, minsnr=1.0, solint=[], combine=""):
        super(Phasecal, self).__init__(selfcal_object.visfile, selfcal_object.imagename, selfcal_object.minblperant,
                                       selfcal_object.refant, selfcal_object.spwmap, selfcal_object.Imager, selfcal_object.want_plot)
        self.calmode = 'p'
        self.minsnr = minsnr
        self.solint = solint
        self.combine = combine
        self.loops = len(self.solint)

    def run(self):
        flagmanager(vis=self.visfile, mode='save',
                    versionname='before_phasecal', merge='replace')
        caltable = ""
        for i in range(0, self.loops):
            imagename = self.imagename + '_ph' + str(i)
            self.Imager.run(imagename)
            caltable = 'pcal' + str(i)
            rmtables(caltable)

            gaincal(vis=self.visfile, caltable=caltable, field=self.Imager.getField(), spw=self.Imager.getSpw(), gaintype='G', refant=self.refant,
                    calmode=self.calmode, combine=self.combine, solint=self.solint[i], minsnr=self.minsnr, minblperant=self.minblperant)

            self.plot_selfcal(caltable, xaxis="time", yaxis="phase", iteration="antenna", subplot=421, plotrange=[0, 0, -180, 180], self.want_plot)

            applycal(vis=self.visfile, field=self.Imager.getField(), spwmap=self.spwmap, gaintable=[
                     caltable], gainfield='', calwt=False, flagbackup=False, interp='linearperobs')

            flagmanager(vis=self.visfile, mode='save',
                        versionname='after_' + caltable)
        return caltable


class AmpPhasecal(Selfcal):
    def __init__(self, selfcal_object, minsnr=1.0, solint=[], combine="", input_caltable=""):
        super(AmpPhasecal, self).__init__(selfcal_object.visfile, selfcal_object.imagename, selfcal_object.minblperant,
                                          selfcal_object.refant, selfcal_object.spwmap, selfcal_object.Imager, selfcal_object.want_plot)
        self.calmode = 'ap'
        self.minsnr = minsnr
        self.solint = solint
        self.combine = combine
        self.input_caltable = input_caltable
        self.loops = len(self.solint)

    def run(self):
        caltable = ""
        for i in range(0, self.loops):
            caltable = 'apcal_' + str(i)
            rmtables(caltable)
            gaincal(vis=self.visfile, field=self.Imager.getField(), caltable=caltable, spw=self.Imager.getSpw(), gaintype='G', refant=self.refant, calmode=self.calmode,
                    combine=self.combine, solint=self.solint[i], minsnr=self.minsnr, minblperant=self.minblperant, gaintable=self.input_caltable, spwmap=self.spwmap, solnorm=True)

            self.plot_selfcal(caltable, xaxis="time", yaxis="amp", iteration="antenna", subplot=421, plotrange=[0, 0, 0.2, 1.8], self.want_plot)

            applycal(vis=self.visfile, spwmap=[self.spwmap, self.spwmap], field=self.Imager.getField(), gaintable=[
                     self.input_caltable, caltable], gainfield='', calwt=False, flagbackup=False, interp='linearperobs')

            flagmanager(vis=self.visfile, mode='save',
                        versionname='after_apcal' + str(i))

            imagename = self.imagename + '_ap' + str(i)

            self.Imager.run(imagename)
