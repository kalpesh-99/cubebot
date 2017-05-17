from flask import request, render_template
from flask_restful import Resource, reqparse
from cubebot_site.model import TriggerModel


#every resrouce has to be a class; here's our first resource
class Trigger(Resource): # so Item iherrits from resrouce
    parser = reqparse.RequestParser()  #this ensures we're only dealing with the price, anything else that comes in gets erased;
    parser.add_argument('category',
        type=str,
        required=True,
        help="The category field cannont be left blank!"
    )

    def post(self, name):
        if TriggerModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400 #400 is for bad request

        data = Trigger.parser.parse_args()

        trigger = TriggerModel(name, data['category'])

		## ah ha the --- try / except (try/catch?) block for error detection ##
        try:
        	trigger.save_to_db() ## cleaner code, updaed for SQLAlchemy
        except:
        	return {"message": "An error occured inserting the item."}, 500 #internal server error




		##usind datbase code above, instead of list append
		# items.append(item)
        return trigger.json(), 201		# 201 code for created; 202 is accepted if you're delayed in creating the object


class TriggerList(Resource):
    def get(self):
        context = {'triggers': list(map(lambda x: x.json(), TriggerModel.query.all()))}
        return context, 201
