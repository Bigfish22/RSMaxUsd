import maxUsd
from pxr import Usd, Sdf, UsdRender, UsdGeom
from pymxs import runtime as rt
import traceback

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.name : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Color3f}

class RSRenderSettingsChaser(maxUsd.ExportChaser):
    def __init__(self, factoryContext, *args, **kwargs):
        super(RSRenderSettingsChaser, self).__init__(factoryContext, *args, **kwargs)
        self.stage = factoryContext.GetStage()

    def PostExport(self):
        try:
            if "Redshift" not in rt.getClassName(rt.renderers.current):
                return False
                
                
            UsdGeom.Scope.Define(self.stage, "/Render")
            UsdGeom.Scope.Define(self.stage, "/Render/Products")
            UsdGeom.Scope.Define(self.stage, "/Render/Products/Vars")
            
            #This holds render settings
            renderSettings = UsdRender.Settings.Define(self.stage, "/Render/Redshift1")
            renderSettingsPrim = self.stage.GetPrimAtPath("/Render/Redshift1")  #I thought inheritance was supposed to make it so I don't have to do chaotic stuff...
            props = rt.getPropNames(rt.renderers.current)
            for prop in props:
                #TODO: Remap any render settings where the names do not match max.
                propAttr = getattr(rt.renderers.current, str(prop))
                type = rt.classOf(propAttr)
                if type == rt.name:
                    propAttr = str(propAttr)
                if type == rt.color:
                    propAttr = (propAttr.r/255, propAttr.g/255, propAttr.b/255)

                renderSettingsPrim.CreateAttribute("redshift:global:" + str(prop), maxTypeToSdf[type]).Set(propAttr)

            #Render Product (the actual target to disk
            renderProduct = UsdRender.Product.Define(self.stage, "/Render/Products/MultiLayer")
            renderSettings.CreateProductsRel().AddTarget("/Render/Products/MultiLayer")
            
            #Aovs and there associated settings
            colorAov = UsdRender.Var.Define(self.stage, "/Render/Products/Vars/color")
            colorAov.CreateSourceNameAttr().Set("color")
            #colorAov.CreateDataTypeAttr()
            colorAov.CreateSourceTypeAttr().Set("raw")
            orderedVarsRel = renderProduct.GetOrderedVarsRel()
            orderedVarsRel.AddTarget("/Render/Products/Vars/color")

            
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
        
        return True
        
maxUsd.ExportChaser.Register(RSRenderSettingsChaser, "RSRenderSettingsChaser", "Redshift object Properties", "Chaser to export RS Object properties")