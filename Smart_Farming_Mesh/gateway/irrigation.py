"""Gateway-level irrigation control logic (software status only)."""
class IrrigationController:
    def __init__(self, dry_threshold=30, wet_threshold=45):
        self.mode = 0  # 0=AUTO, 1=MANUAL
        self.manual_state = 0
        self.dry_threshold = dry_threshold
        self.wet_threshold = wet_threshold
        self.status = 0

    def update_commands(self, mode=None, manual_state=None, dry_threshold=None):
        if mode is not None:
            self.mode = 1 if int(float(mode)) == 1 else 0
        if manual_state is not None:
            self.manual_state = 1 if int(float(manual_state)) == 1 else 0
        if dry_threshold is not None:
            self.dry_threshold = min(40, max(5, int(float(dry_threshold))))
            self.wet_threshold = min(60, self.dry_threshold + 15)

    def decide(self, moisture_values):
        if self.mode == 1:
            self.status = self.manual_state
        elif moisture_values:
            average = sum(moisture_values) / len(moisture_values)
            if average < self.dry_threshold:
                self.status = 1
            elif average >= self.wet_threshold:
                self.status = 0
        return self.status
