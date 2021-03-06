class MyHttpHandler(BaseHTTPRequestHandler):
    def __init__(self,  *args):
      """ change Player for encoder """
      self.logger = logger or logging.getLogger(__name__)
      BaseHTTPRequestHandler.__init__(self, *args)
      self.running = False
      global lg

    def log_message(self, format, *args):
      return

    #Handler for the GET requests
    def do_GET(self):
        # do something with uri
        self.logger.info("GOT URL: %s" %  self.path)
        try:
            if self.path == "/AmpON":
                self.logger.info("Starting AMP")
                GPIO.output(AmpPin, GPIO.HIGH)
                self._return_200()
            elif self.path == "/AmpOFF":
                if not lg.running:
                  self.logger.info("Stopping AMP")
                  GPIO.output(AmpPin, GPIO.LOW)
                  self._return_200()
                else:
                  self.logger.info("Stopping AMP - ignored")
                  self._return_200()
            else:
                self.logger.info("Somethings fishy")
                return self._return_404()
        except ValueError:
            pass

    def _return_200(self):
        self.logger.debug("Responding 200")
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("ok\n")

    def _return_404(self):
        self.logger.debug("Responding 404")
        self.send_response(404)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("URL %s not found\n" % self.path)

class HTTPServerV6(HTTPServer):
  address_family = socket.AF_INET6

class MyHttpServer:
    """ HTTP Server for changing the active player """

    def __init__(self,logger=None):
        self.logger = logger or logging.getLogger(__name__)

        # start http server for Jive remote
        self.t = Thread(target=self._select_player, args=())
        self.t.start()

    def _select_player(self):
        """ Waits on http for the active player """

        self.http_server = HTTPServerV6(('::', http_server_port), MyHttpHandler)
        self.logger.info('Http Server started on port %i' % http_server_port)

        #Wait forever for incoming http requests
        self.logger.debug("HTTP Server Thread started")
        try:
            self.http_server.serve_forever()
        except Exception as e:
            self.logger.debug("Http Server closed")
            pass

    def AmpOn(self):
      self.logger.debug(dir(self.http_server))

    def AmpOff(self):
      self.logger.debug(dir(self.http_server))

    def destroy(self):
        self.http_server.socket.close()


