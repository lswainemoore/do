import rumps

import do

# rumps.debug_mode(True)


class DoStatusBarApp(rumps.App):
    def __init__(self):
        super(DoStatusBarApp, self).__init__('do')
        self.timer = rumps.Timer(self.tick, 1)
        self.menu = ['start']
        self.timer.start()

    @rumps.clicked('start')
    def start(self, _):
        do.block_sites()
        self.timer.start()

    def tick(self, timer):
        rotate = True
        session = do.get_open_session()
        if session:
            if session.is_elapsed:
                self.timer.stop()
                if session.mode == 'blocking':
                    window = rumps.Window(
                        title='BLOCK elapsed',
                        message='',
                        ok='take break',
                        cancel='re-up!',
                        dimensions=(0, 0),    # removes text box
                    )
                    window.add_button('i\'m done')
                    resp = window.run()
                    if resp.clicked == 1:
                        do.unblock_sites()
                        do.start_break()
                        timer.start()
                    elif resp.clicked == 0:
                        do.block_sites()
                        timer.start()
                    elif resp.clicked == 2:
                        do.unblock_sites()
                else:
                    window = rumps.Window(
                        message='BREAK elapsed',
                        ok='let\'s do',
                        cancel='i\'m done',
                    )
                    resp = window.run()
                    if resp.clicked == 1:
                        do.end_break()
                        do.block_sites()
                        timer.start()
                    elif resp.clicked == 0:
                        do.end_break()

        session = do.get_open_session()
        if session:
            self.menu['start'].set_callback(None)
            self.title = f'{session.mode}: {str(int(session.time_left.seconds / 60))}'
        else:
            self.timer.stop()
            self.menu['start'].set_callback(self.start)
            self.title = 'do'


if __name__ == "__main__":
    DoStatusBarApp().run()
