using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using WINX32Lib;

namespace WinspecCOMTest
{
	public partial class Form1 : Form
	{
		private WINX32Lib.Winx32App app;
		private WINX32Lib.IDocFile doc;

		public Form1()
		{
			InitializeComponent();
			app = new WINX32Lib.Winx32App();
		}

		private void button1_Click(object sender, EventArgs e)
		{
			ExpSetup exp;
			exp = new ExpSetup();
			exp.Start(ref doc);

			short pret;
			while (true)
			{
				exp.GetParam(EXP_CMD.EXP_RUNNING_EXPERIMENT, out pret);
				if (pret ==0)
					break;
			}
		}


	}
}
