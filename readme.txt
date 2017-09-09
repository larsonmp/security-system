TODO
--------------------------------------------------------------------------------
1. daemon
2. SSL
3. AuthN
4. AuthZ


ReST API
--------------------------------------------------------------------------------
GET    /camera :list<id>

GET    /camera/<id>/info               :dict
POST   /camera/<id>/snapshot           :id #take new snapshot; POST data = {count}
GET    /camera/<id>/snapshot/<id>      :image
DELETE /camera/<id>/snapshot/<id>
GET    /camera/<id>/snapshot/<id>/info :dict

GET    /camera/<id>/stream #possible?

GET    /thermometer :list<id>

GET    /thermometer/<id>                       :measurement
GET    /thermometer/<id>/info                  :dict
GET    /thermometer/<id>/<year>                :list<measurements> #weekly avg?
DELETE /thermometer/<id>/<year>                #delete cache
GET    /thermometer/<id>/<year>/<month>        :list<measurements> #daily avg?
DELETE /thermometer/<id>/<year>/<month>        #delete cache
GET    /thermometer/<id>/<year>/<month>/<day>  :list<measurements>

GET    /motion/events      :map<id, events>
GET    /motion/events/<id> :dict

GET    /led            :list<dict>
GET    /led/id         :status
POST   /led/id(status)

GET    /status         ?

