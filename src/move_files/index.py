import json
import os
import sys
import time

import dropbox

app_info = json.loads(open("./credentials.json").read())

dbx = dropbox.Dropbox(app_info["accessToken"])
paths = app_info["paths"]


def get_file_names_to_move(folder_name=None, cursor=None):
    if cursor is not None:
        continuing_list = dbx.files_list_folder_continue(cursor)
    else:
        continuing_list = dbx.files_list_folder(folder_name)

    files = [_file.path_lower for _file in continuing_list.entries]
    if continuing_list.has_more:
        files.extend(get_file_names_to_move(cursor=continuing_list.cursor))
    return files


def move_and_wait_until_complete(reloc_paths):
    if len(reloc_paths) == 0:
        print("Nothing to move")
        return
    job_status = dbx.files_move_batch(reloc_paths, autorename=True)
    if not job_status.is_async_job_id():
        print("Job already complete!")
        return
    jobid = job_status.get_async_job_id()
    print(f"Executing with jobid({jobid})")
    print("Checking status: ")
    while 1:
        status = dbx.files_move_batch_check(jobid)
        if not (status.is_complete() or status.is_failed()):
            sys.stdout.write("...")
            sys.stdout.flush()
            time.sleep(1)
            continue

        if status.is_complete():
            print(f"\nJob id ({jobid}) complete")
            print(f"{len(reloc_paths)} files moved")
        else:
            print(f"\nJob id ({jobid}) failed")
            print(status.get_failed())
        break


def folder_of_file(afile):
    bn = os.path.basename(afile)
    year_month_day = bn.split()[0]
    month_year = "-".join(year_month_day.split("-")[:2])
    return month_year


def handler(event, context):
    for path in paths:
        folder_name = path["sourceFolder"]
        destination_folder = path["destinationFolder"]
        files_to_move = get_file_names_to_move(folder_name=folder_name)
        print(f"{len(files_to_move)} files to move from {folder_name}")
        relocation_paths = list(
            map(
                lambda x: dropbox.files.RelocationPath(
                    x,
                    os.path.join(
                        destination_folder, folder_of_file(x), os.path.basename(x)
                    ),
                ),
                files_to_move,
            )
        )
        move_and_wait_until_complete(relocation_paths)


if __name__ == "__main__":
    handler(None, None)
