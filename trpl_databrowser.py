from ScopeFoundry.data_browser import DataBrowser

from viewers.apd_confocal_npz import ApdConfocalNPZView
from viewers.picoharp_npz import PicoHarpNPZView
from viewers.hyperspec_npz import HyperSpecNPZView
from viewers.trpl_npz import TRPLNPZView
from plimg_microscope.picoharp_mcl_2d_slow_scan import Picoharp_MCL_2DSlowScan_View


if __name__ == '__main__':
    import sys
    
    app = DataBrowser(sys.argv)
    app.load_view(ApdConfocalNPZView(app))
    app.load_view(PicoHarpNPZView(app))
    app.load_view(HyperSpecNPZView(app))
    app.load_view(TRPLNPZView(app))
    app.load_view(Picoharp_MCL_2DSlowScan_View(app))
    
    sys.exit(app.exec_())