import maxUsd
from pxr import Usd, Sdf, UsdRender, UsdGeom, Gf
from pymxs import runtime as rt
import traceback

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.name : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Color3f}
                    
aovSourceMap = {}

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
            renderSettings.CreateResolutionAttr().Set(Gf.Vec2i(rt.renderWidth, rt.renderHeight))
            renderSettingsPrim = self.stage.GetPrimAtPath("/Render/Redshift1")  #I thought inheritance was supposed to make it so I don't have to do chaotic stuff...
            props = rt.getPropNames(rt.renderers.current)

            for prop in props:
                try:
                    #TODO: Remap any render settings where the names do not match max.
                    propAttr = getattr(rt.renderers.current, str(prop))
                    type = rt.classOf(propAttr)
                    if type == rt.name:
                        propAttr = str(propAttr)
                    if type == rt.color:
                        propAttr = (propAttr.r/255, propAttr.g/255, propAttr.b/255)

                    renderSettingsPrim.CreateAttribute("redshift:global:" + str(prop), maxTypeToSdf[type]).Set(propAttr)
                except:
                    pass

            #Render Product (the actual target to disk
            renderProduct = UsdRender.Product.Define(self.stage, "/Render/Products/MultiLayer")
            renderProduct.CreateResolutionAttr().Set(Gf.Vec2i(rt.renderWidth, rt.renderHeight))
            self.generateFilePaths(renderProduct)
            renderSettings.CreateProductsRel().AddTarget("/Render/Products/MultiLayer")
            
            #Beauty pass setup
            colorAov = UsdRender.Var.Define(self.stage, "/Render/Products/Vars/color")
            colorAov.CreateSourceNameAttr().Set("color")
            colorAov.CreateDataTypeAttr().Set("color4f")
            colorAov.CreateSourceTypeAttr().Set("raw")
            
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:clearValue", Sdf.ValueTypeNames.Int).Set(0)
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:format", Sdf.ValueTypeNames.Token).Set("color4h")
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:multiSampled", Sdf.ValueTypeNames.Bool).Set(False)
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:name", Sdf.ValueTypeNames.String).Set("rgba")
            
            
            orderedVarsRel = renderProduct.GetOrderedVarsRel()
            orderedVarsRel.AddTarget("/Render/Products/Vars/color")
            
            #Aovs and there associated settings
            ElementManager = rt.maxOps.GetCurRenderElementMgr()
            for i in range(0, ElementManager.NumRenderElements()):
                rendElement = ElementManager.GetRenderElement(i)
                aovPath = Sdf.Path("/Render/Products/Vars").AppendPath(rendElement.elementName)
                aov = UsdRender.Var.Define(self.stage, aovPath)
                aov.CreateSourceNameAttr().Set("color")
                print(rt.classOf(rendElement))
                orderedVarsRel.AddTarget(aovPath)

            
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
        
        return True
        
    def generateFilePaths(self, renderProduct):
        productName = renderProduct.CreateProductNameAttr()
        if rt.rendTimeType == 1:
            productName.Set(rt.rendOutputFilename)
            return
        elif rt.rendTimeType == 2:
            for i in range(int(rt.animationRange.start.frame), int(rt.animationRange.end.frame) + 1):
                pathSplit = os.path.splitext(rt.rendOutputFilename)
                productName.Set(f"{pathSplit[0]}_{i:0>{4}}{pathSplit[1]}", i)
            return
        elif rt.rendTimeType == 3:
            for i in range(int(rt.rendStart.frame), int(rt.rendEnd.frame) + 1):
                pathSplit = os.path.splitext(rt.rendOutputFilename)
                productName.Set(f"{pathSplit[0]}_{i:0>{4}}{pathSplit[1]}", i)
            return
        return
            
        
        
maxUsd.ExportChaser.Register(RSRenderSettingsChaser, "RSRenderSettingsChaser", "Redshift object Properties", "Chaser to export RS Object properties")