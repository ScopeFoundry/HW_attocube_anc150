import numpy as np
import time
from PySide import QtCore

from ScopeFoundry import Measurement

class ExampleScan(Measurement):

    name = "example_scan"

    def setup(self):

        self.display_update_period = 0.1 #seconds

        #connect events

        # local logged quantities

        # connect to gui

        self.dh.connect_bidir_to_widget(self.gui.ui.dh_doubleSpinBox)
        self.dv.connect_bidir_to_widget(self.gui.ui.dv_doubleSpinBox)


    def setup_figure(self):
        self.fig = self.gui.add_figure('example_scan', self.gui.ui.example_scan_plot_widget)
        self.ax = self.fig.add_subplot(111)
        raise NotImplementedError()

    def pre_scan_setup(self):
        pass
        #raise NotImplementedError()
        # hardware
        # create data arrays
        # update figure

    def collect_pixel(self, i_h, i_v):
        # collect data
        # store in arrays
        #raise NotImplementedError()
        pass

    def _run(self):
        #hardware
        #self.stage = self.gui.mcl_xyz_stage_hc
        #self.nanodrive = self.stage.nanodrive

        # Data arrays
        self.h_array = np.arange(self.h0.val, self.h1.val, self.dh.val, dtype=float)
        self.v_array = np.arange(self.v0.val, self.v1.val, self.dv.val, dtype=float)

        self.Nh = len(self.h_array)
        self.Nv = len(self.v_array)

        self.range_extent = [self.h0.val, self.h1.val, self.v0.val, self.v1.val]

        self.corners =  [self.h_array[0], self.h_array[-1], self.v_array[0], self.v_array[-1]]

        self.imshow_extent = [self.h_array[ 0] - 0.5*self.dh.val,
                              self.h_array[-1] + 0.5*self.dh.val,
                              self.v_array[ 0] - 0.5*self.dv.val,
                              self.v_array[-1] + 0.5*self.dv.val]

        #scan specific setup
        self.pre_scan_setup()

        print "scanning"
        try:
            v_axis_id = self.stage.v_axis_id
            h_axis_id = self.stage.h_axis_id

            # move slowly to start position
            start_pos = [None, None,None]
            start_pos[v_axis_id-1] = self.v_array[0]
            start_pos[h_axis_id-1] = self.h_array[0]
            self.nanodrive.set_pos_slow(*start_pos)

            # Scan!
            line_time0 = time.time()

            for i_v in range(self.Nv):
                if self.interrupt_measurement_called:
                    break

                self.v_pos = self.v_array[i_v]
                self.nanodrive.set_pos_ax(self.v_pos, v_axis_id)
                #self.read_stage_position()

                if i_v % 2: #odd lines
                    h_line_indicies = range(self.Nh)[::-1]
                else:       #even lines -- traverse in opposite direction
                    h_line_indicies = range(self.Nh)

                for i_h in h_line_indicies:
                    if self.interrupt_measurement_called:
                        break

                    self.h_pos = self.h_array[i_h]
                    self.nanodrive.set_pos_ax(self.h_pos, h_axis_id)

                    # collect data
                    self.collect_pixel(i_h, i_v)

                print "line time:", time.time() - line_time0
                print "pixel time:", float(time.time() - line_time0)/self.Nh
                line_time0 = time.time()

                # read stage position every line
                self.stage.x_position.read_from_hardware()
                self.stage.y_position.read_from_hardware()
                self.stage.z_position.read_from_hardware()

        #scanning done
        #except Exception as err:
        #    self.interrupt()
        #    raise err
        finally:
            #save  data file
            self.save_data()
    def save_data(self):

        save_dict = {
                 'h_array': self.h_array,
                 'v_array': self.v_array,
                 'Nv': self.Nv,
                 'Nh': self.Nh,
                 'range_extent': self.range_extent,
                 'corners': self.corners,
                 'imshow_extent': self.imshow_extent,
                    }

        for lqname,lq in self.gui.logged_quantities.items():
            save_dict[lqname] = lq.val

        for hc in self.gui.hardware_components.values():
            for lqname,lq in hc.logged_quantities.items():
                save_dict[hc.name + "_" + lqname] = lq.val

        for lqname,lq in self.logged_quantities.items():
            save_dict[self.name +"_"+ lqname] = lq.val

        self.fname = "%i_%s.npz" % (time.time(), self.name)
        np.savez_compressed(self.fname, **save_dict)
        print self.name, "saved:", self.fname

        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            pass


