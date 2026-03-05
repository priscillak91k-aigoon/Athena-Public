import asyncio
import sys
from scripts.parallel_orchestrator import parallel_reasoning

query = "Deep dive into generating fast, 'easy money' to fund a $1500 NZD Mini PC for a local AI server. The user is Priscilla (Cilla): works retail 4 days a week, highly capable but scatterbrained (COMT G/G), avoidant attachment, needs low-friction, highly automated or asynchronous passive income streams. We already have an Etsy 'Lobotto Prints' with 15 products ready to launch. What are the absolute best, easiest, highest-leverage paths to $1500 using my current AI capabilities?"

async def main():
    result = await parallel_reasoning(query, '')
    with open('.context/state/revenue_synthesis_final.txt', 'w', encoding='utf-8') as f:
        f.write(result)

if __name__ == '__main__':
    asyncio.run(main())
