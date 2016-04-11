from zeiss_sem_remcon32 import ZeissSEMRemCon32

rem=ZeissSEMRemCon32('COM4')
resp=rem.write_stigmatorY(4)
print(resp)