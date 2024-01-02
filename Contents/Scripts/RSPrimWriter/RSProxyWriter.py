import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom
from pxr import Gf as pyGf
import pymxs
import traceback


class RSProxyWriter(maxUsd.PrimWriter):
    def GetPrimType(self):
        return "Xform"

    def Write(self, prim, applyOffset, time):
        try: 
            nodeHandle = self.GetNodeHandle()
            stage = prim.GetStage()
            opts = self.GetExportArgs()
            node = rt.maxOps.getNodeByHandle(nodeHandle)
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False

    @classmethod
    def CanExport(cls, nodeHandle, exportArgs):
        node = rt.maxOps.getNodeByHandle(nodeHandle)
        if rt.classOf(node) == rt.RedshiftProxy:
            return maxUsd.PrimWriter.ContextSupport.Supported
        return maxUsd.PrimWriter.ContextSupport.Unsupported
   
# Register the writer.
# First argument is the class, second argument is the Writer name, which will be used as an ID internaly.
maxUsd.PrimWriter.Register(RSProxyWriter, "RSProxyWriter")