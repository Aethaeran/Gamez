

# i tried to use the http status codes that reselbe the issue the most
#http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
WANTED = 100
SNATCHED = 102
DOWNLOADED = 201
COMPLETED = 200 # downloaded and pp_success
PP_FAIL = 502 # post processing failed

#order is / will not be importend ! just for validating its in "range"
ALL_STATUS = (WANTED, SNATCHED, DOWNLOADED, COMPLETED, PP_FAIL)

STATUS_NAMES = {WANTED: 'Wanted', SNATCHED: 'Snatched', DOWNLOADED: 'Downloaded', COMPLETED: 'Completed', PP_FAIL: 'Post Processing Fail'}
SELECTABLE_STATUS = [WANTED, SNATCHED, DOWNLOADED]
