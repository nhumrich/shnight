from json import JSONDecodeError

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from shnight import routes
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware


middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

app = Starlette(middleware=middleware)


@app.exception_handler(JSONDecodeError)
async def bad_json(request, exc):
    return JSONResponse({'reason': 'invalid json', 'details': str(exc)}, status_code=400)


@app.exception_handler(404)
async def serve_index_on_unknown_routes(request, exc):
    return JSONResponse({'message': 'not found'}, status_code=404)


@app.exception_handler(400)
async def handle_malformed_request(request, exc):
    return JSONResponse({'message': exc.detail}, status_code=400)

app = routes.registration(app)


def main():
    kwargs = {'reload': True}
    uvicorn.run('shnight.core:app', host='0.0.0.0', http='h11', port=3988, headers=[('Server', 'shnight')],
                proxy_headers=True, **kwargs)


if __name__ == '__main__':
    main()
