"""Sensor for fdmealplanner account status."""
from datetime import timedelta
import logging
import requests
import arrow
import xmltodict, json
from xml.etree import ElementTree
from itertools import islice
import urllib.parse

from time import mktime

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.util.dt import utc_from_timestamp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

CONF_ACCOUNTS = "accounts"

ICON = "mdi:robot-outline"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCOUNTS, default=[]): vol.All(cv.ensure_list, [cv.string]),
    }
)


BASE_INTERVAL = timedelta(hours=6)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the fdmealplanner platform."""
    
    entities = [fdmealplannerSensor(hass, account) for account in config.get(CONF_ACCOUNTS)]
    if not entities:
        return
    async_add_entities(entities, True)

    # Only one sensor update once every 60 seconds to avoid
    entity_next = 0



class fdmealplannerSensor(Entity):
    """A class for the mealviewer account."""

    def __init__(self, hass, account):
        """Initialize the sensor."""
        
        self._account = account
        self._lunch0 = None
        self._lunch1 = None
        self._lunch2 = None
        self._lunch3 = None
        self._lunch4 = None
        self._state = None
        self._name = self._account
        self.hass = hass
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def entity_id(self):
        """Return the entity ID."""
        #return f"sensor.mealviewer_{self._name}"
        return 'sensor.fdmealplanner_' + (self._account).replace("/","_")
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def should_poll(self):
        """Turn off polling, will do ourselves."""
        return True
        
    async def async_update(self):
        """Update device state."""
        
        self._state = 'Not Updated'
        try:
           
            headers = {
                'accept': 'application/json',
                'pragma': 'no-cache',
                'x-jsonresponsecase': 'camel',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'okhttp/4.9.1',
            }
            session = async_get_clientsession(self.hass)
            [accountId, locationId, mealPeriodId] = self._account.split('/')
            for day in range(5):
                tomorrow = arrow.utcnow().to('US/Eastern').shift(days=day)
                meal = ''
                if tomorrow.weekday() not in (5, 6):
                    formatted_tomorrow = urllib.parse.quote(tomorrow.format('MM DD YYYY'))
                    formatted_year = tomorrow.format('YYYY')
                    formatted_month = tomorrow.format('M')   
                    
                    url = 'https://apiservicelocators.fdmealplanner.com/api/v1/data-locator-webapi/3/meals?accountId=' + accountId + '&endDate=' + formatted_tomorrow + '&isActive=true&isStandalone&locationId='+ locationId +'&mealPeriodId=' + mealPeriodId + '&menuId=0&monthId=' +formatted_month+ '&selectedDate=' + formatted_tomorrow + '&startDate=' + formatted_tomorrow + '&tenantId=3&timeOffset=300&year=' + formatted_year
                    
                    resp = await session.get(url,headers=headers)
                    datajson = await resp.json()
                    
                    if datajson['result'][0].get('xmlMenuRecipes') is None:
                        meal = ''
                    else:                   
                        root = ElementTree.fromstring(datajson['result'][0].get('xmlMenuRecipes'))
                        meal = tomorrow.format('dddd')
                        counter = 0
                        lastEntree = ''
                        for child in root: #islice(root,15):
                            if counter > 5:
                                break
                            entree = child.attrib.get('ComponentEnglishName').strip()
                            is_show_on_menu = child.attrib.get('IsShowOnMenu', '0').strip()
                            if is_show_on_menu != '1':
                                continue
                            if entree == lastEntree:
                                continue
                            lastEntree = entree    
                            counter = counter + 1
                            if counter == 1:
                                meal = meal + ': ' + entree
                            else:
                                meal = meal + ', ' + entree
                            
                            
                
                if day == 0:
                    self._lunch0 = meal
                if day == 1:
                    self._lunch1 = meal
                if day == 2:
                    self._lunch2 = meal
                if day == 3:
                    self._lunch3 = meal
                if day == 4:
                    self._lunch4 = meal
                    
                self._state = 'Updated'    
        except:        
            self._lunch0 = None
            self._lunch1 = None
            self._lunch2 = None
            self._lunch3 = None
            self._lunch4 = None
            
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attr = {}
        
        attr["lunch0"] = self._lunch0
        attr["lunch1"] = self._lunch1    
        attr["lunch2"] = self._lunch2
        attr["lunch3"] = self._lunch3
        attr["lunch4"] = self._lunch4
        
 
        return attr

    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON
