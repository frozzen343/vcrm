import requests

from vcrm.settings import Integration


def bitrix_request(url: str, method: str = 'GET', params: dict = None):
    """
    Get request to Bitrix API.
    GET by default
    """
    if Integration.bitrix_enabled:
        try:
            bitrix_url = f'{Integration.bitrix_url}/{url}'
            if method == 'POST':
                response = requests.post(bitrix_url, params=params)
            else:
                response = requests.get(bitrix_url, params=params)
            data = response.json()
            return data

        except (requests.exceptions.ConnectionError,
                requests.exceptions.RequestException) as err:  # connection err
            return err

        except KeyError:
            return 'KeyError'

    return False


def get_task_by_id(task_id):
    """
    Get task by ID

    Returns:
        ?
    """
    url = f'tasks.task.get.json?taskId={task_id}'

    data = bitrix_request(url)

    return data


def get_task_list_by_activity():
    """
    Check last tasks by activity
    """
    # select specific fields
    field_select = ('select[ID]=ID&'
                    'select[TITLE]=TITLE&'
                    'select[STATUS]=STATUS&'
                    'select[COMMENTS_COUNT]=COMMENTS_COUNT&'
                    'select[CREATED_BY]=CREATED_BY&'
                    'select[DESCRIPTION]=DESCRIPTION&'
                    'select[CREATED_DATE]=CREATED_DATE')
    # serviceCommentsCount
    field_order = 'order[CHANGED_DATE]=desc'
    field_filter = f'filter[GROUP_ID]={Integration.bitrix_group_id}'

    url = f'tasks.task.list.json?{field_select}&{field_filter}&{field_order}'

    data = bitrix_request(url)

    return data


def set_task_accept(task_id):
    """
    Set task status to accept
    """
    # or tasks.task.approve
    url = f'tasks.task.start.json?taskId={task_id}'
    data = bitrix_request(url, method='POST')
    return data


def set_task_close(task_id):
    """
    Set task status to complete
    """
    url = f'tasks.task.complete.json?taskId={task_id}'
    data = bitrix_request(url, method='POST')
    return data


def set_task_renew(task_id):
    """
    Set task status to accept again
    """
    url = f'tasks.task.renew.json?taskId={task_id}'
    data = bitrix_request(url, method='POST')
    return data


def get_task_comment(task_id):
    """
    Get list of task comments
    """
    url = f'task.commentitem.getlist.json?TASKID={task_id}'
    data = bitrix_request(url)
    return data


def add_task_comment(task_id, comment: str):
    """
    Add task comment
    """
    params = {'FIELDS[POST_MESSAGE]': comment}
    url = f'task.commentitem.add.json?TASKID={task_id}'
    data = bitrix_request(url, 'POST', params=params)
    return data
