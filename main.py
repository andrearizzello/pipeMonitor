from string import Template
from requests import get
import rumps
import sys

project_id = 0
headers = None
base_url = ""


def printHelp():
    print(Template("PipeMonitor help:\n"
                   "You must provide a valid base url, a project id and a valid token\n"
                   "python3 $program_name *base_url* *project_id* *personal_access_tokens*")
          .safe_substitute(program_name=sys.argv[0]))


def openPipeline(pipeline):
    r = get(Template('https://$base_url/api/v4/projects/$proj_id/pipelines/$idpipe')
            .safe_substitute(base_url=base_url,
                             idpipe=pipeline.idPipeline,
                             proj_id=project_id), headers=headers)
    result = r.json()
    window = rumps.Window(cancel=None, ok="Close")
    window.title = Template("Pipeline N: $pipelineid").safe_substitute(pipelineid=result["id"])
    window.default_text = Template("Status:         $status\n"
                                   "Created by: $creator\n"
                                   "Web URL:    $url").safe_substitute(status=result["status"],
                                                                       creator=result["user"]["name"],
                                                                       url=result["web_url"])
    window.run()


def getPipelines():
    r = get(Template('https://$base_url/api/v4/projects/$proj_id/pipelines')
            .safe_substitute(base_url=base_url, proj_id=project_id), headers=headers)
    return r.json()


def getMenuPipelines():
    pipelines = getPipelines()
    final_list_pipelines = []
    for pipeline in pipelines:
        tmp = rumps.MenuItem(Template('Pipeline N: $number  status: $status')
                             .safe_substitute(number=pipeline["id"],
                                              status="✅" if pipeline["status"] == 'success' else "❌"),
                             callback=openPipeline)
        tmp.idPipeline = pipeline["id"]
        final_list_pipelines.append(tmp)
    return final_list_pipelines


if __name__ == "__main__":
    if len(sys.argv) < 4 or not sys.argv[2].isdigit():
        printHelp()
        exit(1)
    base_url = sys.argv[1]
    project_id = sys.argv[2]
    headers = {'PRIVATE-TOKEN': sys.argv[3]}
    program = rumps.App(name="PipeMonitor", title="PipeMonitor", icon="gitlab.jpg")
    program.menu = ["Loading pipelines..."]
    program.menu.clear()
    program.menu.update(getMenuPipelines())
    program.run()
