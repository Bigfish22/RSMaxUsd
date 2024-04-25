import maxUsd
from pxr import Usd, Sdf
from pymxs import runtime as rt
import traceback

class RSImportChaser(maxUsd.ImportChaser):
    def __init__(self, factoryContext, *args, **kwargs):
        super(RSImportChaser, self).__init__(factoryContext, *args, **kwargs)

        self.primsToNodeHandles = factoryContext.GetPrimsToNodeHandles()

        self.stage = factoryContext.GetStage()
        
    def PostImport(self):
        try:
            for prim_path, node_handle in self.primsToNodeHandles.items():
                node = rt.maxOps.getNodeByHandle(node_handle)
                prim = self.stage.GetPrimAtPath(prim_path)
                
                #RS Mesh Params
                tessAttr = prim.GetAttribute("primvars:redshift:object:RS_objprop_rstess_enable")
                dispAttr = prim.GetAttribute("primvars:redshift:object:RS_objprop_displace_enabl")
                if tessAttr or dispAttr:
                    meshParams = rt.RedshiftMeshParams()
                    rt.addModifier(node, meshParams)
                    



        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
        return True


maxUsd.ImportChaser.Register(RSImportChaser, "RSImportChaser", "Import RS object properties", "Import RS object properties")