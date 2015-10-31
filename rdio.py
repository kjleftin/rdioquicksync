require 'net/http'
require 'uri'

class Rdio:
    """Connects to the Rdio API via OAuth2.0.
    
    Logged in user requests are not supported.
    """

    TOKEN_ENDPOINT = 'https://services.rdio.com/oauth2/token'
    RESOURCE_ENDPOINT = 'https://services.rdio.com/api/1/'
    
    def __init__(self, clientId, clientSecret):
        self.clientId = clientId
        self.clientSecret = clientSecret
    
    def get_access_token(self):
        """Returns the string access token

        Gets a client access token.
        """
        url = urlparse(TOKEN_ENDPOINT))
        http = Net::HTTP.new(url.host, url.port)
        http.use_ssl = true
        req = Net::HTTP::Post.new(url.path)
        req.basic_auth(@clientId, @clientSecret)
        req.set_form_data({'grant_type' => 'client_credentials'})
        res = http.request(req)
        JSON.parse(res.body)['access_token']

    def call(self, method, params={}):
        params = params.clone
        params['method'] = method
        params['access_token'] = get_access_token()
        
        url = URI.parse(RESOURCE_ENDPOINT)
        http = Net::HTTP.new(url.host, url.port)
        http.use_ssl = true
        req = Net::HTTP::Post.new(url.path)
        req.set_form_data(params)
        res = http.request(req)
        JSON.parse(res.body)

