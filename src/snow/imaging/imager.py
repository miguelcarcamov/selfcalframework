from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from dataclasses import field as _field

from typing import Union

from astropy.units import Quantity

from ..utils import (calculate_number_antennas, calculate_psnr_fits, calculate_psnr_ms)


@dataclass(init=True, repr=True)
class Imager(metaclass=ABCMeta):
    """
        General Imager object

        Parameters
        ----------
        inputvis :
            Absolute path to the input Measurement Set file
        output :
            Absolute path to the output
        cell :
            Cellsize - example: cell=[’0.5arcsec,’0.5arcsec’] or
            cell=[’1arcmin’, ’1arcmin’] cell = ’1arcsec’ is equivalent to [’1arcsec’,’1arcsec’]
        robust :
            Robustness parameter for Briggs weighting.
            robust = -2.0 maps to uniform weighting. robust = +2.0 maps to natural weighting.
        weighting :
            Weighting scheme (natural,uniform,briggs,superuniform,radial). During gridding of the dirty
            or residual image, each visibility value is multiplied by a weight before it is accumulated on the uv-grid.
            The PSF’s uv-grid is generated by gridding only the weights (weightgrid).
        field :
            Select field
        spw :
            Select spectral window/channels
        stokes :
            Stokes planes to reconstruct
        phase_center :
            Phase center of the image
        data_column :
            Data column to use for image synthesis
        M :
            Horizontal image size
        N :
            Vertical image size
        niter :
            Number of iterations
        noise_pixels :
            Pixels where to calculate the noise on the residual image. Default is None, and it means to
            calculate the RMS on the whole image
        save_model :
            Whether to save the model column or not
        verbose :
            Whether to use verbose option for imagers
    """
    inputvis: str = ""
    output: str = ""
    cell: str = ""
    robust: float = 2.0
    weighting: str = "briggs"
    field: str = ""
    spw: str = ""
    stokes: str = "I"
    phase_center: str = ""
    data_column: str = "corrected"
    M: int = 512
    N: int = 512
    reference_freq: Union[str, float, Quantity, None] = None
    niter: int = 100
    noise_pixels: int = None
    save_model: bool = True
    verbose: bool = True
    psnr: float = _field(init=False, default=0.0)
    peak: float = _field(init=False, default=0.0)
    stdv: float = _field(init=False, default=0.0)
    name: float = _field(init=False, default="")
    nantennas: int = _field(init=False, default=0)

    def __post_init__(self):
        if self.inputvis is not None and self.inputvis != "":
            self.nantennas = calculate_number_antennas(self.inputvis)

    def _calculate_statistics_fits(
        self, signal_fits_name="", residual_fits_name="", stdv_pixels=None
    ) -> None:
        """
        Calculates the peak signal-to-noise ratio, peak and rms for a FITS image.

        Parameters
        ----------
        signal_fits_name :
            Absolute path to the restored FITS image
        residual_fits_name :
            Absolute path to the residual FITS image
        stdv_pixels :
            Pixels where to calculate the RMS
        """
        if stdv_pixels is None:
            psnr, peak, stdv = calculate_psnr_fits(
                signal_fits_name, residual_fits_name, self.noise_pixels
            )
        else:
            psnr, peak, stdv = calculate_psnr_fits(
                signal_fits_name, residual_fits_name, stdv_pixels
            )

        self.psnr = peak / stdv
        self.peak = peak
        self.stdv = stdv

    def _calculate_statistics_msimage(
        self, signal_ms_name="", residual_ms_name="", stdv_pixels=None
    ) -> None:
        """
        Calculates the peak signal-to-noise ratio, peak and rms for a CASA image.

        Parameters
        ----------
        signal_ms_name :
            Absolute path to the restored CASA image
        residual_ms_name :
            Absolute path to the residual CASA image
        stdv_pixels :
            Pixels where to calculate the RMS
        """
        if stdv_pixels is None:
            psnr, peak, stdv = calculate_psnr_ms(
                signal_ms_name, residual_ms_name, self.noise_pixels
            )

        self.psnr = peak / stdv
        self.peak = peak
        self.stdv = stdv

    def _check_reference_frequency(self):
        aux_reference_freq = ""
        if self.reference_freq is not None:
            if isinstance(self.reference_freq, Quantity) or isinstance(self.reference_freq, float):
                aux_reference_freq = str(self.reference_freq)
            elif self.reference_freq is None:
                aux_reference_freq = ""
            elif isinstance(self.reference_freq, str):
                aux_reference_freq = self.reference_freq
            else:
                raise NotImplementedError(
                    "Type {} has not implementation in snow".format(type(self.reference_freq))
                )
        return aux_reference_freq

    @abstractmethod
    def run(self, imagename=""):
        return
