# fry
*All right! I'm a delivery boy!*

![Image of Fry](images/fry.png)

## Description
Fry is an extension of the python requests library with two primary goals:
- Manage stat tracking for requests made through the FrySession
- Internally manage dependency settings within the FrySession

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

fsession = fry.FrySession(stats_client=StatsdClient('example'), adapter_settings=adapter_settings)

signature = 'Example.example'
request_params = {'test': 'value'}

response = fsession.make_request('GET', 'http://www.example.com', signature, params=request_params)

```

## Development
Update the version when updating the library in: `fry/__init__.py`

Build the library locally: `python setup.py sdist`
