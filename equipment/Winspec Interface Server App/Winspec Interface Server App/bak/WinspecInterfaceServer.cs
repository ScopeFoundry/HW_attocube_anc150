using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

using System.Runtime.InteropServices;
using WINX32Lib;
using tcpServer;

namespace WinspecCOMTest
{
    internal unsafe struct DataHeader
    {
        public int total_size;   // Total size of the transmission including this uint
        public int data_type;    // Data type
        public int xdim;
        public int ydim;
        public double intg_time;
        public double grating_pos;
        public fixed double calib_coeffs[5];
        public int frame_count;
        public int data_size;
    }

	class WinspecInterfaceServer
	{
		private WINX32Lib.Winx32App app;
		private WINX32Lib.IDocFile doc;
        private WINX32Lib.ExpSetup exp;
        private WINX32Lib.SpectroObjMgrClass spec;

        private TcpServer server;

        public WinspecInterfaceServer()
        {
            // Build the TCP/IP Server and connect the event handlers
            server = new TcpServer();
            server.OnConnect += this.OnConnect_Handler;
            server.OnDataAvailable += this.OnDataAvailable_Handler;
            server.OnError += this.OnError_Handler;

            // Setup the Winspec interface
            doc = null; //Initialize the current doc to null;
            app = new Winx32App();   // Will either launch or connect to the current Winspec instance
            exp = new ExpSetup();
            spec = new SpectroObjMgrClass();
        }

        public void open(int port)
        {
            // Start the server
            server.Port = port;
            server.Open();
        }

        public void close()
        {
            server.Close();
        }

        ~WinspecInterfaceServer()
        {
            app = null;
            exp = null;
            server.Close();
        }

        private void OnConnect_Handler(TcpServerConnection connection)
        {
            return;
        }

        private void OnDataAvailable_Handler(TcpServerConnection connection)
        {
            // Incoming command.  Read until EOF is reached.
            NetworkStream stream = connection.Socket.GetStream();
            byte[] data;
            List<byte[]> chunks = new List<byte[]>();
            int read_count;
            string s;
            string command = "";

            do {
                data = new byte[1000];
                read_count = stream.Read(data, 0, 1000);
                s = Encoding.ASCII.GetString(data, 0, read_count);
                
                // See if we found a complete command.
                int i_eof;
                i_eof = s.IndexOf("\n"); 

                if (i_eof > -1)
                {
                    command += s.Substring(0, i_eof);
                    process_command(ref command, connection);
                    
                    if (i_eof < read_count-1) {
                        command = s.Substring(i_eof+1, read_count - i_eof+1);
                    } else {
                        command = "";
                    }
                }
            } while (stream.DataAvailable);
        }

        private void OnError_Handler(TcpServer server, Exception e)
        {
            return;
        }

        private void process_command(ref string full_command, TcpServerConnection connection)
        {
            string[] command_elements = full_command.Split(' ');

            switch (command_elements[0].ToLower())
            {
                case "acquire":
                    if (is_acquiring())
                        send_response("err already acquiring\n", connection);
                    else
                        start_acquisition();
                        send_response("ok\n", connection);
                    break;

                case "status":
                    if (is_acquiring())
                        send_response("1\n", connection);
                    else
                        send_response("0\n", connection);
                    break;

                case "get_data":
                    if (is_acquiring())
                    {
                        send_response("err acquiring\n", connection);
                        break;
                    }
                    else if (doc == null)
                    {
                        send_response("err no data available\n", connection);
                        break;
                    }
                    else
                    {
                        send_current_data(connection);
                    }
                    break;
                case "set_acq_time":
                    try
                    {
                        object obj = Convert.ToDouble(command_elements[1]);
                        exp.SetParam(EXP_CMD.EXP_EXPOSURE, ref obj);
                        send_response("ok\n", connection);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine("Error setting acquisition time\n");
                        send_response("err " + e.Message + "\n", connection);
                    }
                    break;
                
                case "get_acq_time":
                    try
                    {
                        short res;
                        double acq_time_out = (double)exp.GetParam(EXP_CMD.EXP_EXPOSURE, out res);
                        send_response(String.Format("ok {0}\n", acq_time_out), connection);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine("Error fetching acquisition time\n");
                        send_response("err " + e.Message + "\n", connection);
                    }
                    break;

                case "set_grating":
                    try
                    {
                        object grating = Convert.ToInt32(command_elements[1]);
                        object position = Convert.ToDouble(command_elements[2]);
                        spec.Current.SetParam(SPT_CMD.SPT_NEW_GRATING, ref grating);
                        spec.Current.SetParam(SPT_CMD.SPT_NEW_POSITION, ref position);
                        spec.Current.Move();
                        send_response("ok\n", connection);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine("Error setting grating\n");
                        send_response("err " + e.Message + "\n", connection);
                    }
                    break;

                case "get_grating":
                    try
                    {
                        object grating = new object();
                        object position = new object();
                        spec.Current.GetParam(SPT_CMD.SPT_INST_CUR_GRAT_NUM, 0, out grating);
                        spec.Current.GetParam(SPT_CMD.SPT_INST_CUR_GRAT_POS, 0, out position);
                        send_response(string.Format("ok {0} {1}\n", grating, position), connection);
                    }
                     catch (Exception e)
                    {
                        Console.WriteLine("Error fetching grating\n");
                        send_response("err " + e.Message + "\n", connection);
                    }
                    break;

                case "reinitialize":
                    try
                    {
                        // Setup the Winspec interface
                        doc = null; //Initialize the current doc to null;
                        app = new Winx32App();   // Will either launch or connect to the current Winspec instance
                        exp = new ExpSetup();
                        spec = new SpectroObjMgrClass();
                        send_response(string.Format("ok\n", grating, position), connection);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine("Error reinitialzing winspec automation objects\n");
                        send_response("err " + e.Message + "\n", connection);
                    }
                    break;
            }
        }

        private void send_response(string response, TcpServerConnection connection)
        {
            try
            {
                NetworkStream stream = connection.Socket.GetStream();

                byte[] bytes;

                bytes = Encoding.UTF8.GetBytes(response.ToCharArray(), 0, response.Length);
                stream.Write(bytes, 0, response.Length);
            }
            catch (Exception e)
            {
                Console.WriteLine("Error sending response: " + e.Message);
            }
        }

        private void send_current_data(TcpServerConnection connection)
        {
            NetworkStream stream = connection.Socket.GetStream();

            // Build the header structure for the data packet
            DataHeader header = new DataHeader();
            short res;
            header.xdim = (int)doc.GetParam(DM_CMD.DM_XDIM, out res);
            header.ydim = (int)doc.GetParam(DM_CMD.DM_YDIM, out res);
            header.frame_count = (int)doc.GetParam(DM_CMD.DM_FRAMECOUNT, out res);
            header.data_type = (int)doc.GetParam(DM_CMD.DM_DATATYPE, out res);
            object obj1 = doc.GetParam(DM_CMD.DM_SPECCENTERWLNM, out res);
            header.intg_time = (double)doc.GetParam(DM_CMD.DM_EXPOSEC, out res);
            header.grating_pos = (double)doc.GetParam(DM_CMD.DM_SPECCENTERWLNM, out res);

            // Calibration values
            CalibObj calib = doc.GetCalibration();
            unsafe
            {
                for (int i = 0; i < 5; i++)
                    header.calib_coeffs[i] = calib.PolyCoeffs[i];
            }

            // Figure out how many bytes are needed for the data based on the data type.
            int pixel_count = header.xdim * header.ydim * header.frame_count;
            int frame_pixel_count = header.xdim * header.ydim;
            int frame_byte_size = 0;
            switch (header.data_type)
            {
                case 1:
                    // int16
                    header.data_size = sizeof(short)*pixel_count;
                    frame_byte_size = sizeof(short) * frame_pixel_count;
                    break;
                case 2:
                    // int32
                    header.data_size = sizeof(int) * pixel_count;
                    frame_byte_size = sizeof(int) * frame_pixel_count;
                    break;
                case 3:
                    // float32
                    header.data_size = sizeof(float) * pixel_count;
                    frame_byte_size = sizeof(float) * frame_pixel_count;
                    break;
                case 5:
                    // byte
                    header.data_size = sizeof(byte) * pixel_count;
                    frame_byte_size = sizeof(byte) * frame_pixel_count;
                    break;
                case 6:
                    // uint16
                    header.data_size = sizeof(ushort)*pixel_count;
                    frame_byte_size = sizeof(ushort)*frame_pixel_count;
                    break;
            }

            // Write the header structure:
            int header_size = Marshal.SizeOf(header);
            byte[] header_bytes = new byte[header_size];
            IntPtr ptr = Marshal.AllocHGlobal(header_size);
            Marshal.StructureToPtr(header, ptr, true);
            Marshal.Copy(ptr, header_bytes, 0, header_size);
            try
            {
                stream.Write(header_bytes, 0, header_size);
            }
            catch (Exception e)
            {
                Console.Write("Failed to write data header to stream: " + e.Message);
                return;
            }


            // Write the frame data to the socket
            object obj = null;
            byte[] frame_bytes = new byte[frame_byte_size];
            for (int i_frame = 1; i_frame <= header.frame_count; i_frame++)
            {
                doc.GetFrame(1, ref obj);
                Buffer.BlockCopy((Array)obj, 0, frame_bytes, 0, frame_byte_size);
                try
                {
                    stream.Write(frame_bytes, 0, frame_byte_size);
                }
                catch (Exception e)
                {
                    Console.Write("Failed to write frame data to stream:  " + e.Message);
                }
            }
        }

        private void start_acquisition()
        {
            exp = new ExpSetup();
            exp.Start(ref doc);
        }

        private bool is_acquiring()
        {
            short p_val;
            exp.GetParam(EXP_CMD.EXP_RUNNING_EXPERIMENT, out p_val);

            return p_val == 1;
        }



	}
}
