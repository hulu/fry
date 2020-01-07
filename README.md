# fry
*All right! I'm a delivery boy!*

![Image of Fry](images/fry.png)

## Description
Fry is an extension of the python requests library built to better manage service-level http interactions.
- Manages dependency settings within the Session object, lessening the amount of overhead boilerplate code
    - Dependency settings include retry count and timeout; split per host
- Given a statsd object, will also record and report stats per request; split per endpoint

StatsD libraries currently supported:
- datadog

## Usage
```python
import fry

adapter_settings = {
    'http://www.example.com': {
        'retry': {
            'total': 3,
            'read': 3
        },
        'adapter': {
            'pool_maxsize': 4,
        },
        'adapter_config': {
            'timeout': 0.5
        }
    }
}

fsession = fry.FrySession(stats_client=DogStatsd('example'), adapter_settings=adapter_settings)

signature = 'hostname.endpoint'
request_params = {'test': 'value'}

response = fsession.make_request('GET', 'http://www.example.com', signature, params=request_params)

```

## Development
Update the version when updating the library in: `fry/__init__.py`

Build the library locally: `python setup.py sdist`

## Change Log
### 0.2.0
* Support for datadog statsd api
