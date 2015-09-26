import h5py
import time

"""
recommended HDF5 file format for ScopeFoundry
* = group
- = attr
D = data_set

* /
    - scope_foundry_version = 100
    - emd_version = 102
    * gui
        - log_quant_1
        - log_quant_1_unit
        - ...
    * hardware
        * hardware_component_1
            - log_quant_1
            - log_quant_1_unit
            - ...
            * units
                - log_quant_1 = '[n_m]'
        * ...
    * measurement_1
        - log_quant_1
        - ...
        * units
            - log_quant_1 = '[n_m]'
        * image_like_data_set_1
            - emd_group_type = 1
            D data
            D dim0
                - name = 'x'
                - unit = '[n_m]'
            D ...
            D dimN
        D simple_data_set_2
        D ...

other thoughts:
    store git revision of code
    store git revision of ScopeFoundry

"""

def h5_base_file(gui, fname):
    h5_file = h5py.File(fname)
    root = h5_file['/']
    root.attrs["ScopeFoundry_version"] = 100
    t0 = time.time()
    root.attrs['time_id'] = t0

    h5_save_gui_lq(gui, root)
    h5_save_hardware_lq(gui, root)
    return h5_file

def h5_save_gui_lq(gui, h5group):
    h5_gui_group = h5group.create_group('gui/')
    h5_gui_group.attrs['ScopeFoundry_type'] = "Gui"
    settings_group = h5_gui_group.create_group('settings')
    h5_save_lqs_to_attrs(gui.logged_quantities, settings_group)


def h5_save_hardware_lq(gui, h5group):
    h5_hardware_group = h5group.create_group('hardware/')
    h5_hardware_group.attrs['ScopeFoundry_type'] = "HardwareList"
    for hc_name, hc in gui.hardware_components.items():
        h5_hc_group = h5_hardware_group.create_group(hc_name)
        h5_hc_group.attrs['name'] = hc.name
        h5_hc_group.attrs['ScopeFoundry_type'] = "Hardware"
        h5_hc_settings_group = h5_hc_group.create_group("settings")
        h5_save_lqs_to_attrs(hc.logged_quantities, h5_hc_settings_group)
    return h5_hardware_group

def h5_save_lqs_to_attrs(logged_quantities, h5group):
    """
    Take a dictionary of logged_quantities
    and create attributes inside h5group

    :param logged_quantities:
    :param h5group:
    :return: None
    """
    unit_group = h5group.create_group('units')
    # TODO decide if we should specify h5 attr data type based on LQ dtype
    for lqname, lq in logged_quantities.items():
        h5group.attrs[lqname] = lq.val
        if lq.unit:
            unit_group.attrs[lqname] = lq.unit


def h5_create_measurement_group(measurement, h5group):
    h5_meas_group = h5group.create_group('measurement/' + measurement.name)
    h5_save_measurement_settings(measurement, h5_meas_group)
    return h5_meas_group

def h5_save_measurement_settings(measurement, h5_meas_group):
    h5_meas_group.attrs['name'] = measurement.name
    h5_meas_group.attrs['ScopeFoundry_type'] = "Measurement"
    settings_group = h5_meas_group.create_group("settings")
    h5_save_lqs_to_attrs(measurement.logged_quantities, settings_group)