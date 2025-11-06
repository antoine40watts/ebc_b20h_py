#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest test suite for physical EBC-B20H device.

Requirements:
- Physical EBC-B20H device connected via USB
- Battery connected to the device (recommended: test battery with known voltage)
- pytest and pytest-asyncio installed

Run with:
    pytest test_ebc_b20h_physical.py -v
    pytest test_ebc_b20h_physical.py -v -k "test_connection"  # Run specific test
    pytest test_ebc_b20h_physical.py -v --tb=short  # Shorter traceback
"""

import pytest
import asyncio
import time
import logging
from typing import List

from ebc_b20h import EBC_B20H

# Configure logging
logging.basicConfig(level=logging.INFO)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def device():
    """Create a single device instance for all tests."""
    ebc = EBC_B20H()
    ebc.connect()
    yield ebc
    # Cleanup
    ebc.stop()
    ebc.destroy()


@pytest.fixture(scope="function")
async def connected_device(device):
    """Ensure device is ready before each test and cleanup after."""
    # Ensure device is stopped and idle
    device.stop()
    await asyncio.sleep(2)
    
    yield device
    
    # Cleanup after test
    device.stop()
    await asyncio.sleep(1)


@pytest.fixture(scope="function")
async def monitoring_device(connected_device):
    """Device with monitoring enabled."""
    datapoints = []
    
    def capture_callback(dp):
        datapoints.append(dp)
    
    await connected_device.new_monitor(capture_callback)
    
    yield connected_device, datapoints
    
    # Stop monitoring
    if connected_device.is_monitoring:
        await connected_device.stop_monitoring()


# ============================================================================
# Connection Tests
# ============================================================================

class TestConnection:
    """Test device connection and basic communication."""
    
    def test_device_found(self):
        """Test that device can be found on USB."""
        ebc = EBC_B20H()
        assert ebc.dev is not None
        ebc.destroy()
    
    def test_connection(self, device):
        """Test device connection."""
        assert device.dev is not None
    
    def test_initial_state(self, device):
        """Test initial device state."""
        assert device.is_charging == False
        assert device.is_discharging == False
        assert device.is_ready == True


# ============================================================================
# Encoding/Decoding Tests
# ============================================================================

class TestEncodingDecoding:
    """Test encoding and decoding functions."""
    
    @pytest.mark.parametrize("voltage,expected_msb,expected_lsb", [
        (2.0, 0, 200),
        (5.0, 2, 8),
        (12.0, 5, 0),
        (24.0, 10, 0),
        (30.0, 12, 120),
    ])
    def test_voltage_encoding(self, voltage, expected_msb, expected_lsb):
        """Test voltage encoding."""
        msb, lsb = EBC_B20H.encode_voltage(voltage)
        assert msb == expected_msb
        assert lsb == expected_lsb
    
    @pytest.mark.parametrize("voltage", [2.0, 5.5, 12.6, 24.3, 48.0])
    def test_voltage_roundtrip(self, voltage):
        """Test voltage encoding/decoding roundtrip."""
        msb, lsb = EBC_B20H.encode_voltage(voltage)
        decoded = EBC_B20H.decode_voltage(msb, lsb)
        assert abs(decoded - voltage) < 0.02  # Allow small tolerance
    
    @pytest.mark.parametrize("current,expected_msb,expected_lsb", [
        (0.1, 0, 10),
        (1.0, 0, 100),
        (5.0, 2, 8),
        (10.0, 4, 16),
        (20.0, 8, 32),
    ])
    def test_current_encoding(self, current, expected_msb, expected_lsb):
        """Test current encoding."""
        msb, lsb = EBC_B20H.encode_current(current)
        assert msb == expected_msb
        assert lsb == expected_lsb
    
    @pytest.mark.parametrize("current", [0.1, 1.0, 5.5, 10.0, 15.5, 20.0])
    def test_current_roundtrip(self, current):
        """Test current encoding/decoding roundtrip."""
        msb, lsb = EBC_B20H.encode_current(current)
        decoded = EBC_B20H.decode_current(msb, lsb)
        assert abs(decoded - current) < 0.01
    
    @pytest.mark.parametrize("mah,expected", [
        (100, (0, 100)),
        (1000, (4, 40)),
        (5000, (20, 200)),
        (9999, (41, 159)),
        (10000, (136, 88)),  # Threshold transition
        (15000, (142, 88)),
        (20000, (148, 88)),
    ])
    def test_mah_encoding(self, mah, expected):
        """Test mAh encoding."""
        msb, lsb = EBC_B20H.encode_mah(mah)
        assert (msb, lsb) == expected
    
    @pytest.mark.parametrize("mah", [100, 1000, 5000, 9999, 10000, 15000, 20000])
    def test_mah_roundtrip(self, mah):
        """Test mAh encoding/decoding roundtrip."""
        msb, lsb = EBC_B20H.encode_mah(mah)
        decoded = EBC_B20H.decode_mah(msb, lsb)
        assert decoded == mah
    
    def test_checksum(self):
        """Test checksum calculation."""
        data = [0x01, 0x04, 0x28, 0x00, 0xC8, 0x00, 0x00]
        expected = 0xE5
        assert EBC_B20H.checksum(data) == expected


# ============================================================================
# Monitoring Tests
# ============================================================================

@pytest.mark.asyncio
class TestMonitoring:
    """Test device monitoring functionality."""
    
    async def test_start_monitoring(self, connected_device):
        """Test starting monitoring."""
        datapoints = []
        
        def callback(dp):
            datapoints.append(dp)
        
        await connected_device.new_monitor(callback)
        assert connected_device.is_monitoring == True
        
        await asyncio.sleep(5)
        
        await connected_device.stop_monitoring()
        assert connected_device.is_monitoring == False
    
    async def test_monitoring_data_format(self, monitoring_device):
        """Test that monitoring returns properly formatted data."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(5)
        
        assert len(datapoints) > 0
        
        # Check datapoint format [voltage, current, mah]
        for dp in datapoints:
            assert len(dp) == 3
            assert isinstance(dp[0], (int, float))  # voltage
            assert isinstance(dp[1], (int, float))  # current
            assert isinstance(dp[2], (int, float))  # mah
    
    async def test_monitoring_voltage_reading(self, monitoring_device):
        """Test that voltage readings are reasonable."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(5)
        
        assert len(datapoints) > 0
        
        # Voltage should be in reasonable range (assuming battery connected)
        for dp in datapoints:
            voltage = dp[0]
            assert 0 <= voltage <= 80  # Max device voltage is 72V


# ============================================================================
# Discharge Tests
# ============================================================================

@pytest.mark.asyncio
class TestDischarge:
    """Test discharge functionality."""
    
    async def test_discharge_command(self, monitoring_device):
        """Test basic discharge command."""
        device, datapoints = monitoring_device
        
        # Get initial voltage
        await asyncio.sleep(3)
        initial_voltage = device.voltage
        
        # Start discharge at 1A to minimum 2V below current
        cutoff_v = max(2.0, initial_voltage - 2.0)
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        
        await asyncio.sleep(5)
        
        # Check device is discharging
        assert device.is_discharging == True
        assert device.current > 0
        
        # Stop discharge
        device.stop()
        await asyncio.sleep(3)
        
        assert device.is_discharging == False
    
    async def test_discharge_current_limits(self, monitoring_device):
        """Test discharge current limiting."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Test with 2A discharge
        device.discharge(current=2.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        
        # Current should be close to 2A (within tolerance)
        assert 1.5 < device.current < 2.5
        
        device.stop()
        await asyncio.sleep(2)
    
    async def test_discharge_continuous(self, monitoring_device):
        """Test continuous discharge mode."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Start first discharge
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(3)
        
        # Change to continuous discharge at different current
        device.discharge(current=2.0, cutoff_v=cutoff_v, cont=True)
        await asyncio.sleep(5)
        
        assert device.is_discharging == True
        assert 1.5 < device.current < 2.5
        
        device.stop()
        await asyncio.sleep(2)
    
    async def test_discharge_to_cutoff(self, monitoring_device):
        """Test discharge stops at cutoff voltage."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        
        # Set cutoff very close to current voltage (will stop quickly)
        cutoff_v = initial_voltage - 0.5
        
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(3)
        
        # Wait for cutoff (timeout after 30 seconds)
        timeout = 30
        start_time = time.time()
        
        while device.is_discharging and (time.time() - start_time) < timeout:
            await asyncio.sleep(2)
        
        # Should have stopped
        assert device.is_discharging == False
        
        # Voltage should be at or below cutoff
        assert device.voltage <= cutoff_v + 0.5  # Small tolerance


# ============================================================================
# Charge Tests
# ============================================================================

@pytest.mark.asyncio
class TestCharge:
    """Test charge monitoring functionality."""
    
    async def test_charge_command(self, monitoring_device):
        """Test basic charge command (requires external charger)."""
        device, datapoints = monitoring_device
        
        # Enable charge monitoring with 0.1A cutoff
        device.charge(cutoff_c=0.1, cont=False)
        
        await asyncio.sleep(5)
        
        # Note: This will only show charging if external charger is active
        # Otherwise device should just be in charge monitoring mode
        
        device.stop()
        await asyncio.sleep(2)


# ============================================================================
# Stop and Control Tests
# ============================================================================

@pytest.mark.asyncio
class TestControl:
    """Test device control commands."""
    
    async def test_stop_command(self, monitoring_device):
        """Test stop command."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Start discharge
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        
        assert device.is_discharging == True
        
        # Stop discharge
        device.stop()
        await asyncio.sleep(3)
        
        assert device.is_discharging == False
        assert device.current < 0.1
    
    async def test_adjust_command(self, monitoring_device):
        """Test adjust command during discharge."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 2.0)
        
        # Start discharge at 1A
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        
        # Adjust to 2A
        device.adjust(current=2.0, cutoff_v=cutoff_v)
        await asyncio.sleep(5)
        
        # Current should be close to 2A
        assert 1.5 < device.current < 2.5
        
        device.stop()
        await asyncio.sleep(2)


# ============================================================================
# State Transition Tests
# ============================================================================

@pytest.mark.asyncio
class TestStateTransitions:
    """Test device state transitions."""
    
    async def test_idle_to_discharge_transition(self, monitoring_device):
        """Test transition from idle to discharge."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        
        # Should be idle
        assert device.is_discharging == False
        assert device.is_charging == False
        
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Start discharge
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        
        # Should be discharging
        assert device.is_discharging == True
        assert device.is_charging == False
        
        device.stop()
        await asyncio.sleep(3)
        
        # Should be idle again
        assert device.is_discharging == False
        assert device.is_charging == False
    
    async def test_ready_flag(self, monitoring_device):
        """Test is_ready flag behavior."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        
        assert device.is_ready == True
        
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Start discharge
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        
        # Wait for ready flag
        timeout = 10
        start_time = time.time()
        while not device.is_ready and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.5)
        
        assert device.is_ready == True
        assert device.is_discharging == True
        
        device.stop()
        await asyncio.sleep(2)


# ============================================================================
# Safety Tests
# ============================================================================

@pytest.mark.asyncio
class TestSafety:
    """Test safety limits and error handling."""
    
    async def test_max_current_limit(self, monitoring_device):
        """Test that current is limited to 20A max."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Try to set 25A (should be capped at 20A)
        device.discharge(current=25.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        
        # Current should not exceed 20A
        assert device.current <= 20.5
        
        device.stop()
        await asyncio.sleep(2)
    
    async def test_min_current_limit(self, monitoring_device):
        """Test that current is limited to 0.1A min."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        cutoff_v = max(2.0, initial_voltage - 1.0)
        
        # Try to set 0.05A (should be capped at 0.1A)
        device.discharge(current=0.05, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        
        if device.is_discharging:
            # Current should be at least 0.1A
            assert device.current >= 0.08
        
        device.stop()
        await asyncio.sleep(2)
    
    async def test_voltage_limits(self, monitoring_device):
        """Test voltage limits."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        
        # Try minimum voltage (2V)
        device.discharge(current=1.0, cutoff_v=1.0, cont=False)  # Should be capped at 2V
        await asyncio.sleep(3)
        device.stop()
        await asyncio.sleep(2)
        
        # Try maximum voltage (72V) - won't reach but should accept
        device.discharge(current=1.0, cutoff_v=80.0, cont=False)  # Should be capped at 72V
        await asyncio.sleep(3)
        device.stop()
        await asyncio.sleep(2)


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
class TestIntegration:
    """Integration tests simulating real usage scenarios."""
    
    async def test_short_discharge_cycle(self, monitoring_device):
        """Test a complete short discharge cycle."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        
        initial_voltage = device.voltage
        initial_mah = device.mah
        
        cutoff_v = max(2.0, initial_voltage - 0.5)
        
        # Discharge for 10 seconds
        device.discharge(current=2.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(10)
        
        # Stop and check results
        device.stop()
        await asyncio.sleep(3)
        
        # Should have consumed some capacity
        assert device.mah > initial_mah
        
        # Voltage should have dropped
        assert device.voltage < initial_voltage
        
        # Check we got datapoints
        assert len(datapoints) > 0
    
    async def test_multiple_operations_sequence(self, monitoring_device):
        """Test multiple sequential operations."""
        device, datapoints = monitoring_device
        
        await asyncio.sleep(2)
        initial_voltage = device.voltage
        
        # Operation 1: Discharge at 1A
        cutoff_v = max(2.0, initial_voltage - 0.3)
        device.discharge(current=1.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        device.stop()
        await asyncio.sleep(3)
        
        # Operation 2: Discharge at 2A
        cutoff_v = max(2.0, device.voltage - 0.3)
        device.discharge(current=2.0, cutoff_v=cutoff_v, cont=False)
        await asyncio.sleep(5)
        device.stop()
        await asyncio.sleep(3)
        
        # Should have collected data
        assert len(datapoints) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
