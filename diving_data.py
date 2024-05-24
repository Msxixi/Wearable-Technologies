import time

class DiveComputer:
    def __init__(self, fo2=0.21):
        self.fo2 = fo2  # Default oxygen fraction is 21%
        self.depth = 0  # Current depth
        self.start_time = None  # Start time of dive
        self.dive_time = 0  # Dive time (minutes)
        self.ascent_rate = 0  # Ascent rate (meters/minute)

    def update_ascent_rate(self, new_rate):
        """
        Update ascent rate
        :param new_rate: New ascent rate (meters/minute)
        """
        self.ascent_rate = new_rate

    def update_depth(self, new_depth):
        """
        Update current depth
        :param new_depth: New depth value (meters)
        """
        self.depth = new_depth

    def start_dive(self):
        """
        Start the dive
        """
        self.start_time = time.time()

    def stop_dive(self):
        """
        End the dive
        """
        self.start_time = None

    def calculate_dive_time(self):
        """
        Calculate real-time dive time
        """
        if self.start_time is not None:
            current_time = time.time()
            self.dive_time = (current_time - self.start_time) / 60  # Convert to minutes

    def calculate_PO2(self):
        """
        Calculate oxygen partial pressure PO2
        :return: Oxygen partial pressure PO2 (ATA)
        """
        p_ambient = 1 + self.depth / 10  # Ambient pressure (ATA)
        po2 = self.fo2 * p_ambient
        return po2

    def calculate_NDL(self):
        """
        Calculate no-decompression limit (NDL), using a simple linear approximation model
        Actual NDL calculation should use dive tables or dive computers
        :return: NDL (minutes)
        """
        if self.depth <= 12:
            ndl = 60
        elif self.depth <= 18:
            ndl = 50
        elif self.depth <= 24:
            ndl = 40
        elif self.depth <= 30:
            ndl = 25
        else:
            ndl = 20
        return ndl

    def calculate_CNS(self):
        """
        Calculate central nervous system toxicity (CNS)
        :return: CNS percentage
        """
        po2 = self.calculate_PO2()
        # Common PO2 and time table (time limit table)
        cns_limits = {
            1.0: 570, 1.1: 480, 1.2: 420, 1.3: 360,
            1.4: 300, 1.5: 240, 1.6: 150, 1.7: 120,
            1.8: 90, 1.9: 60, 2.0: 45, 2.1: 30,
            2.2: 25, 2.3: 20, 2.4: 15, 2.5: 10,
            2.6: 8, 2.7: 6, 2.8: 5, 2.9: 4, 3.0: 3
        }

        # Find appropriate time limit value (using interpolation)
        sorted_po2_keys = sorted(cns_limits.keys())
        limit_time = None
        for i in range(len(sorted_po2_keys) - 1):
            if sorted_po2_keys[i] <= po2 < sorted_po2_keys[i + 1]:
                limit_time = ((cns_limits[sorted_po2_keys[i + 1]] - cns_limits[sorted_po2_keys[i]]) /
                              (sorted_po2_keys[i + 1] - sorted_po2_keys[i]) *
                              (po2 - sorted_po2_keys[i]) + cns_limits[sorted_po2_keys[i]])
                break
        if limit_time is None:
            limit_time = cns_limits[sorted_po2_keys[-1]] if po2 >= sorted_po2_keys[-1] else cns_limits[sorted_po2_keys[0]]

        cns_percentage = (self.dive_time / limit_time) * 100
        return cns_percentage

    def calculate_safe_stop_time(self):
        """
        Calculate safe stop time
        :return: Safe stop time (minutes)
        """
        safety_stop_depth = 3  # Safe stop depth (meters)
        if self.depth > safety_stop_depth:
            stop_time = (self.depth - safety_stop_depth) / self.ascent_rate
        else:
            stop_time = 0
        return stop_time

# Number of records
record_count = 10

# Start calculations automatically
dive_computer = DiveComputer(fo2=0.32)  # Using enriched air, oxygen fraction 32%
dive_computer.start_dive()  # Start the dive

for i in range(record_count):
    # Update depth and dive time (using example values)
    dive_computer.update_depth(i + 1)  # Increase depth by 1 meter each time
    dive_computer.calculate_dive_time()  # Calculate real-time dive time
    dive_computer.update_ascent_rate(9)  # Ascent rate 9 meters/minute

    # Calculate and display results
    po2 = dive_computer.calculate_PO2()
    ndl = dive_computer.calculate_NDL()
    cns_percentage = dive_computer.calculate_CNS()
    safe_stop_time = dive_computer.calculate_safe_stop_time()

    print(f"Current Depth: {dive_computer.depth} meters")
    print(f"Real-time Dive Time: {dive_computer.dive_time:.2f} minutes")
    print(f"PO2: {po2:.2f} ATA")
    print(f"NDL: {ndl} minutes")
    print(f"CNS Toxicity: {cns_percentage:.2f}%")
    print(f"Safe Stop Time: {safe_stop_time:.2f} minutes")
    
    # Output separator line
    print("-" * 50)

    time.sleep(1)  # Update status every 1 second
    dive_computer.depth += 1  # Increase current depth
