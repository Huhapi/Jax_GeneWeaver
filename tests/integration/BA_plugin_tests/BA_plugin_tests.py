# Unit testing for Boolean Algebra
import asyncio
import json
from ATS import ATS_Plugin

from plugins.BooleanAlgebra import BA, service
import asyncio
import json

if __name__ == "__main__":
    async def test():
         ba = BA.BooleanAlgebra()
         
         operations = "intersect"
         at_least_values =  2
                         
                 
         input_data = {
                     "tools_input": "Boolean Algebra",
                     "geneset_ids": ["GS1256", "GS239581", "GS137861"],
                     "relation": operations,
                     "at_least": at_least_values,
                     "print_to_cli": True
                 }
                 
         result = await ba.run(input_data)
                 
         with open('output' + '.json', 'w') as fp:
             json.dump(result.result, fp)
         print(result.result)
         print(f"\nStatus: {ba.status().result}")
     
         asyncio.run(test())