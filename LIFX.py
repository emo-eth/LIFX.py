from BaseAPI import BaseAPI


class LIFX(BaseAPI):
    '''
    Selectors:
    all - All lights belonging to the authenticated account
    label:[value] - Lights that match the label.
    id:[value] - The light with the given id/serial number. Returns a list of
        one light.
    group_id:[value] - The lights belonging to the group with the given ID
    group:[value] - The lights belonging to the groups matching the given label
    location_id:[value] - The lights belonging to the location matching the
        given ID
    location:[value] - The lights belonging to the locations matching the given
        label
    scene_id:[value] - the lights that are referenced in the scene ID'''

    def __init__(self, token):
        (super(LIFX, self)
            .__init__('https://api.lifx.com/v1/',
                      rate_limit_status_code=429,
                      headers={'Authorization': 'Bearer %s' % token},
                      cache_life=-1))

    def list_lights(self, selector='all'):
        '''Lists lights for a given selector
        Params:
            string selector: The selector to limit which light information is
                returned. '''
        query_string = 'lights/' + str(selector) + '/'
        return self._get(query_string)

    def set_state(self, selector='all', power='on', color=None, brightness=1.0,
                  duration=1.0, infrared=None):
        '''Sets the state of the lights within the selector. All parameters
        (except for the selector) are optional. If you don't supply a
        parameter, the API will leave that value untouched.

        Params:
            REQUIRED:
            string selector: The selector to limit which lights are controlled.
            Optional:
            string power: The power state you want to set on the selector. on
                or off
            string color: The color to set the light to.
            double brightness: The brightness level from 0.0 to 1.0. Overrides
                any brightness set in color (if any)
            double duration: How long in seconds you want the power action to
                take. Range: 0.0 – 3155760000.0 (100 years)
            double infrared: The maximum brightness of the infrared channel.'''
        payload = self._parse_payload(locals().copy(),
                                      exclude_endpoints=['selector'])
        endpoint = '/lights/' + str(selector) + '/state'
        return self._put(endpoint, payload)

    def set_states(self, states, defaults={}):
        '''This endpoint allows you to set different states on multiple
        selectors in a single request.

        Each hash in states is comprised of a state hash as per Set State,
        except with the inclusion of selector which you would normally specify
        in the URL in a Set State request.

        You can optionally use the defaults hash to specify the base hash that
        each state hash is built from.

        The API will attempt to execute each operation at the same time but
        does not make any guarantees.

        Params:
            REQUIRED:
            list states: Array of state hashes as per Set State. No more than
                50 entries.
            Optional:
            dict defaults: Default values to use when not specified in each
                states[] object.'''
        assert len(states) <= 50, 'No more than 50 states'
        payload = self._parse_payload(locals().copy())
        endpoint = '/lights/states'
        return self._put(endpoint, payload)

    def toggle_power(self, selector='all', duration=1.0):
        payload = self._parse_payload(locals().copy(),
                                      exclude_endpoints=['selector'])
        endpoint = '/lights/' + str(selector) + '/toggle'
        return self._post(endpoint, payload)

    def breathe(self, color, selector='all', from_color=None, period=1.0,
                cycles=1.0, persist=False, power_on=True, peak=0.5):
        '''Performs a breathe effect by slowly fading between the given colors.
        Use the parameters to tweak the effect.

        Params:
            REQUIRED:
            string selector: The selector to limit which lights will run the
                effect.
            string color: The color to use for the breathe effect.
            Optional:
            string from_color: The color to start the effect from. If this
                parameter is omitted then the color the bulb is currently set
                to is used instead.
            double period: The time in seconds for one cyles of the effect.
            double cycles: The number of times to repeat the effect.
            boolean persist: If false set the light back to its previous value
                when effect ends, if true leave the last effect color.
            boolean power_on: If true, turn the bulb on if it is not already
                on.
            double peak: Defines where in a period the target color is at its
                maximum. Minimum 0.0, maximum 1.0.'''
        payload = self._parse_payload(locals().copy(),
                                      exclude_endpoints=['selector'])
        endpoint = '/lights/' + str(selector) + '/effects/breathe'
        return self._post(endpoint, payload)

    def pulse(self, color, selector='all', from_color=None, period=1.0,
              cycles=1.0, persist=False, power_on=True):
        '''Performs a pulse effect by quickly flashing between the given
        colors. Use the parameters to tweak the effect.

        Params:
            REQUIRED:
            string selector: The selector to limit which lights will run the
                effect.
            string color: The color to use for the breathe effect.
            Optional:
            string from_color: The color to start the effect from. If this
                parameter is omitted then the color the bulb is currently set
                to is used instead.
            double period: The time in seconds for one cyles of the effect.
            double cycles: The number of times to repeat the effect.
            boolean persist: If false set the light back to its previous value
                when effect ends, if true leave the last effect color.
            boolean power_on: If true, turn the bulb on if it is not already
                on.'''
        payload = self._parse_payload(locals().copy(),
                                      exclude_endpoints=['selector'])
        endpoint = '/lights/' + str(selector) + '/effects/breathe'
        return self._post(endpoint, payload)

    def cycle(self):
        '''This endpoint lets you easily have a set of lights transition to the
        next state in a list of states you supply without having to implement
        client side logic to calculate the next state in the sequence.

        For example, you can have a hardware button that will cycle through a
        few different brightness settings and off by simply binding a button
        press to send an identical Cycle request, and the API figures out the
        rest.

        The API scores each state hash against the current states of all the
        lights in the selector, and if the score is high enough to be
        considered a match, it will apply the next state in the list,
        looping back to the first one if necessary. If there's no close match,
        it will apply the closest state to the selector.

        The maximum of 5 states was selected so a user would not have to press
        a button more than 6 times to achieve their desired state.

        The optional direction parameter determines the direction the API uses
        to determine the next state.

        If you have a scenario where the Cycle API does not work as expected,
        please let us know on the forums.

        Params:
            REQUIRED:
            list states: Array of state hashes as per Set State. Must have 2
                to 5 entries.
            Optional:
            dict defaults: Default values to use when not specified in each
                states[] object.
            string direction: Direction in which to cycle through the list.
                Can be forward or backward'''

    def list_scenes(self):
        '''Lists all the scenes available in the users account. Scenes listed
        here can be activated with the Activate Scene endpoint.

        For the purposes of this endpoint the serial_number field on each
        device corresponds to the id field for other endpoints. We are aware
        that this is not optimal and plan to fix this in a later release of the
        HTTP API.'''
        query_string = '/scenes'
        return self._get(query_string)

    def activate_scene(self, scene_uuid, duration=1.0):
        '''
        Activates a scene from the users account
        Params:
            REQUIRED:
            string scene_uuid: The UUID for the scene you wish to activate
            Optional:
            double duration: The time in seconds to spend performing the scene
                transition.'''
        payload = self._parse_payload(locals().copy(),
                                      exclude_endpoints=['scene_uuid'])
        endpoint = 'scenes/scene_id:%s/activate' % scene_uuid
        return self._put(endpoint, payload)

    def validate_color(self, string):
        '''This endpoint lets you validate a user's color string and return the
        hue, saturation, brightness and kelvin values that the API will
        interpret as.
        Params:
            REQUIRED:
            string string: Color string you'd like to validate'''
        params = self._parse_params(locals().copy())
        query_string = 'color' + params
        return self._get(query_string)
