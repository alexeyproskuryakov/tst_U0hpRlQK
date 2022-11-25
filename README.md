# Test work.

API server with two endpoints. Has configuration file with rpc endpoints for available networks (see `config.yaml`).  

## Endpoints

`GET /balance` with query parameters: `address`, `block_number`, `network`.

Returns balance in `wei` for needed address at used block number (default `latest`) in used network (default `AVAX`). 


`GET /events` with query parameter: `block_number`.

Returns events of contract since block number.  


