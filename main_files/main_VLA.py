from selfcalframework.imaging import Clean
from selfcalframework.selfcalibration import AmpPhasecal, Phasecal

if __name__ == '__main__':
    visfile = sys.argv[3]
    output = sys.argv[4]
    want_plot = eval(sys.argv[5])

    # Table for automasking on long or short baselines can be found here: https://casaguides.nrao.edu/index.php/        Automasking_Guide
    # The default clean object will use automasking values for short baselines
    # In this case we will use automasking values for long baselines

    clean_imager = Clean(
        inputvis=visfile,
        output=output,
        niter=100,
        M=1024,
        N=1024,
        cell="0.3arcsec",
        stokes="I",
        datacolumn="corrected",
        robust=0.5,
        specmode="mfs",
        deconvolver="hogbom",
        gridder="standard",
        pbcor=True,
        savemodel=True,
        usemask='auto-multithresh',
        sidelobethreshold=1.25,
        noisethreshold=5.0,
        minbeamfrac=0.1,
        lownoisethreshold=2.0,
        negativethreshold=0.0,
        interactive=True
    )

    shared_vars_dict = {
        'visfile': clean_imager.getVis(),
        'minblperant': 4,
        'refant': "VA05",
        'spwmap': [0, 0, 0, 0],
        'gaintype': 'G',
        'want_plot': want_plot
    }

    #solint_phs = ['128s', '64s', '32s', '16s']
    solint_phs = ['inf']
    solint_amp = ['1h']
    solint_ap = ['inf']

    phscal = Phasecal(
        minsnr=3.0, solint=solint_phs, combine="spw", Imager=clean_imager, **shared_vars_dict
    )

    phscal.run()

    # ampcal = Ampcal(minsnr=2.0, solint=solint_amp, combine="scan",
    #                selfcal_object=parent_selfcal, input_caltable=phs_caltable)

    #amp_caltable = ampcal.run()

    apcal = AmpPhasecal(
        minsnr=3.0,
        solint=solint_ap,
        combine="",
        selfcal_object=phscal,
        Imager=clean_imager,
        **shared_vars_dict
    )

    apcal.run()

    apcal.selfcal_output(overwrite=True)
