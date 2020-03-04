 
# SecurityCAT Gateway
 
 ### Prerequisities
 * Installed Python libraries `pip install -r requirements.txt`
 * Redis
 * the ```securityrat_url``` variable in ```gateway.py``` set to the URL of your actual SecurityRAT instance
 
 ### How to launch
1. Launch your Redis instance (local port 6379 is expected by default)
2. CD into the directory
3. Start Celery ```celery worker -A gateway.celery --loglevel=info --pool=solo```
> `--pool=solo` only starts one thread to avoid value unpacking problem on windows
4. Starting testing MS: ```python3 ./microservice.py``` 
5. Starting gateway:  ```python3 ./gateway.py``` 
