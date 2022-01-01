import todoist
 
lbls = {}
noteDict = {}

def printtask(depth, item):
    lbl = ""
    for ls in item['labels']:
        lbl += lbls[ls] + ":"
    if(lbl != ""):
        lbl = "\t\t\t\t:" + lbl
    state = "TODO" if item['checked'] == 0 else "DONE"
    print("{} {} {} {}".format("*" * depth, state, item['content'], lbl))
    if('due' in item and item['due'] != None):
        date = item['due']
        print(" " * depth + " SCHEDULED: <{}>".format(date)) 
    print(" " * depth + " :PROPERTIES:")
    print(" " * depth + "   :URL: [[https://todoist.com/app/project/{}/task/{}][Task]]".format(item['project_id'],item['id']))
    print(" " * depth + "   :TODOISTID: {}".format(item['id']))
    print(" " * depth + " :END:")
    if(item['description'].strip() != ""):
        print(" " * depth + " " + item['description'])
    if(item['id'] in noteDict):
        notes = noteDict[item['id']]
        for n in notes:
            print(" " * depth + " [{}]".format(n['posted']))
            print(" " * depth + " #+BEGIN_QUOTE")
            print(" " * depth + " {}".format(n['content']) )
            print(" " * depth + " #+END_QUOTE")

def print_subtasks(depth, parent, prj, api):
    for item in api.state['items']:
        if(parent['id'] == item['parent_id']):
            if(('is_archived' not in item or item['is_archived'] == 0) and ('is_deleted' not in item or item['is_deleted'] == 0)):
                print(str(item))
                printtask(depth, item)
                print_subtasks(depth+1, item, prj, api)

def syncme(token):
    api = todoist.api.TodoistAPI(token)
    api.sync()
    global lbls
    prjs = {}
    global noteDict
    noteDict = {}
    for label in api.state['labels']:
        lbls[label['id']] = label['name']
    for note in api.state['notes']:
        i = note['item_id']
        if i not in noteDict:
            noteDict[i] = []
        noteDict[i].append(note)
    for project in api.state['projects']:
        prjs[project['id']] = {"name": project['name'], 'id': project['id']}
        #print(str(project))
        #print(project['name'])
    print("#+TITLE: Todoist - {}".format(api.state['user']['full_name']))
    # print(str(api.state))
    # This is a key that can be used to track changes on the remote site.
    print("#+TODOIST_SYNC: {}".format(api.sync_token))
    for idx,prj in prjs.items():
        if(('is_archived' in prj and prj['is_archived'] != 0) or ('is_deleted' in prj and prj['is_deleted'] != 0)):
            continue
        if(prj['name'] != "Personal"):
            continue
        print("* TODO " + prj['name'])
        print("  :PROPERTIES:")
        print("    :URL: [[https://todoist.com/app/project/{}][Project]]".format(prj['id']))
        print("    :TODOISTID: {}".format(prj['id']))
        print("  :END:")
        for item in api.state['items']:
           if(item['parent_id'] == prj['id'] or (item['parent_id'] == None and item['project_id'] == prj['id'])):
                    if(('is_archived' not in item or item['is_archived'] == 0) and ('is_deleted' not in item or item['is_deleted'] == 0)):
                        #print(str(item))
                        printtask(2, item)
                        print_subtasks(3, item, prj, api)
                #print(str(item))
                #print("** TODO " + item['content'])
    pass

syncme(token)

