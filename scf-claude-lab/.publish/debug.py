import asyncio
from api.main import run_policy_tests
from api.schemas import PolicyTestsRequest

async def run():
    req = PolicyTestsRequest(
        control_id="SCF-001",
        run_positive_tests=True,
        run_negative_tests=True
    )
    res = await run_policy_tests(req)
    print("SUCCESS:", dict(res))

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        import traceback
        traceback.print_exc()
