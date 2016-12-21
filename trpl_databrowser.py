from ScopeFoundry.data_browser import DataBrowser

from viewers.apd_confocal_npz import ApdConfocalNPZView
from viewers.picoharp_npz import PicoHarpNPZView
from viewers.hyperspec_npz import HyperSpecNPZView
from viewers.trpl_npz import TRPLNPZView
from plimg_microscope.picoharp_mcl_2d_slow_scan import Picoharp_MCL_2DSlowScan_View
from measurement_components.apd_confocal import APD_MCL_2DSlowScanZView
from df_microscope.winspec_remote_2Dscan import WinSpecMCL2DSlowScanView
from df_microscope.winspec_remote_readout import WinSpecRemoteReadoutView


if __name__ == '__main__':
    import sys
    
    app = DataBrowser(sys.argv)
    app.load_view(ApdConfocalNPZView(app))
    app.load_view(PicoHarpNPZView(app))
    app.load_view(HyperSpecNPZView(app))
    app.load_view(TRPLNPZView(app))
    app.load_view(Picoharp_MCL_2DSlowScan_View(app))
    app.load_view(APD_MCL_2DSlowScanZView(app))
    app.load_view(WinSpecMCL2DSlowScanView(app))
    app.load_view(WinSpecRemoteReadoutView(app))
    
    sys.exit(app.exec_())