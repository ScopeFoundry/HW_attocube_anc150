using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using WinspecInterfaceService;

namespace WinspecCOMTest
{
	public partial class Form1 : Form
	{
        private WinspecInterfaceServer ws_server;

		public Form1()
		{
			InitializeComponent();

            ws_server = new WinspecInterfaceServer();
            ws_server.Log += OnLog_Handler;
            ws_server.open(9000);
		}

        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            ws_server.close();
        }

        private void OnLog_Handler(object sender, LogEventArgs e)
        {
            Console.WriteLine(e.Text);
        }

        private void button_exit_Click(object sender, EventArgs e)
        {
            this.Close();
        }
	}
}
