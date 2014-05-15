import jinja2

class HtmlLog:
    def __init__(self, template="standard"):
        template_file = "standard.html"
        
        template_loader = jinja2.FileSystemLoader(searchpath="templates")
        template_environment = jinja2.Environment(loader=template_loader)
        self.template = template_environment.get_template(template_file)
        
        self.template_vars = {}
        
    def initTemplateGlobals(self, customer):
        self.template_vars["customer"] = customer
    
    def 
    
    def cookTemplate(self):
        outputText = self.template.render(self.template_vars)
        print outputText
        
if __name__ == "__main__":
    htmlLog = HtmlLog()
    htmlLog.initTemplateGlobals(customer="Jeremy")
    htmlLog.cookTemplate()