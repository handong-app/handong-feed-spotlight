from fastapi import FastAPI

from app.api.v1.endpoints.healthcheck_router import healthcheck_router
from app.api.v1.endpoints.test_router import test_router


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 서버 시작시 실행
#     task = asyncio.create_task(run_annoy_index_update())
#     yield
#     # 서버 종료시 실행
#     task.cancel()

app = FastAPI()
# lifespan 활성화 하려면, 아래 코드 주석해제.
# app = FastAPI(lifespan=lifespan)

# async def run_annoy_index_update():
#     while True:
#         subprocess.run(["python", "util/build_annoy_index_last_14days.py"], check=True)
#         print("Annoy index updated successfully")
#         await asyncio.sleep(86400)  # 24시간

app.include_router(test_router, prefix="/api/test")
app.include_router(healthcheck_router, prefix="/api/healthcheck")
