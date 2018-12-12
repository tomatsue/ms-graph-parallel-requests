import concurrent.futures
import json
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer

import settings
from graph_client import GraphClient
from utils import build_filters


def get_sing_ins(client):
    query = {'$top': 999}
    results = client.get('/auditLogs/signIns', query)

    return results


def get_sing_ins_multithread(client, max_workers):
    filter_property = 'createdDateTime'
    today = datetime.today()
    borders = sorted([str((today - timedelta(days=i)).date())
                      for i in range(30)])
    querys = [{'$top': 999, '$filter': filter}
              for filter in build_filters(filter_property, borders)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_results = [executor.submit(
            client.get, '/auditLogs/signIns', query) for query in querys]
        results = [future.result()
                   for future in concurrent.futures.as_completed(future_to_results)]

    return sum(results, [])


if __name__ == '__main__':
    start = timer()

    graph_client = GraphClient(
        tenant_name=settings.TENANT_NAME,
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        logging_enable=settings.LOGGING_ENABLED
    )
    multi_thread_enabled = settings.MULTI_THREAD_ENABLED
    multi_thread_max_workers = settings.MULTI_THREAD_MAX_WORKERS

    print(f'THREADING_ENABLED: {multi_thread_enabled}')
    if multi_thread_enabled:
        print(f'THREADING_MAX_WORKERS: {multi_thread_max_workers}')
        results = get_sing_ins_multithread(graph_client, multi_thread_max_workers)
    else:
        results = get_sing_ins(graph_client)

    results = sorted(results, key=lambda x: x['createdDateTime'])

    end = timer()
    print(f'elapsed_time: {end - start:.2f} secs')

    # save the results
    output_file = settings.OUTPUT_FILE
    with open(output_file, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=4,
                  sort_keys=True, separators=(',', ': '))
    print(f"Saved the results as '{output_file}'")
