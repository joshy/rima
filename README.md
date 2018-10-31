RIMA - Radiology IMage Analysis

Research prototype for Radiology image processing.

Prerequistes
 * Redis

For searching the PACS use [Meta](https://github.com/joshy/meta). This will
allow you with the latest version to analyze exams for example for
COPD (LAA values).


For downloading the images from the PACS [MOVA](https://github.com/joshy/mova)
is used. One the data is downloaded it is processed with RIMA. The processing
is done via pydicom and other python libs. For orchestration
[luigi](https://github.com/spotify/luigi) is used.



To actuall run the task COPD task run:
```
env PYTHONPATH=. luigi --module  watcher COPDWatcher --local-scheduler
```

Currently implemented algorithms:
 * COPD: calculation of LAA values