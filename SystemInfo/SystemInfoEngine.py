import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et
import platform,socket,re,uuid,json,logging, psutil, getpass
from datetime import datetime
import time
import os

class AyxPlugin:
    def __init__(self, n_tool_id: int, alteryx_engine: object, output_anchor_mgr: object):
        # Default properties
        self.n_tool_id: int = n_tool_id
        self.alteryx_engine: Sdk.AlteryxEngine = alteryx_engine
        self.output_anchor_mgr: Sdk.OutputAnchorManager = output_anchor_mgr

        pass

    def pi_init(self, str_xml: str):
        self.output_anchor = self.output_anchor_mgr.get_output_anchor('Output')
        self.processes = Et.fromstring(str_xml).find('processes').text == 'True' if 'processes' in str_xml else None
        self.services = Et.fromstring(str_xml).find('services').text == 'True' if 'services' in str_xml else None
        self.environ = Et.fromstring(str_xml).find('environ').text == 'True' if 'environ' in str_xml else None
        pass

    def pi_add_incoming_connection(self, str_type: str, str_name: str) -> object:
        return self

    def pi_add_outgoing_connection(self, str_name: str) -> bool:
        return True

    def get_size(self, bytes, suffix="B"):
        """
        Scale bytes to its proper format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f} {unit}{suffix}"
            bytes /= factor

    def getSystemInfo(self):
        try:
            info=[]
            #general info
            info.append(('General','User', getpass.getuser()))
            info.append(('General', 'Current Time', datetime.now().strftime('%Y/%m/%#d %H:%M:%S')))

            #Platform Info
            info.append(('Platform', 'Platform', platform.platform()))
            info.append(('Platform', 'System', platform.system()))
            info.append(('Platform', 'Platform-release', platform.release()))
            info.append(('Platform', 'Platform-version', platform.version()))
            info.append(('Platform', 'Architecture', platform.machine()))
            info.append(('Platform', 'Hostname', socket.gethostname()))
            info.append(('Platform', 'IP-address', socket.gethostbyname(socket.gethostname())))
            info.append(('Platform', 'MAC-address', ':'.join(re.findall('..', '%012x' % uuid.getnode()))))
            info.append(('Platform', 'Processor', platform.processor()))
            info.append(('Platform', 'RAM', self.get_size(psutil.virtual_memory().total)))

            # boot time
            boot_time_timestamp = psutil.boot_time()
            bt = datetime.fromtimestamp(boot_time_timestamp)
            info.append(('Platform', 'Boot Time', bt.strftime('%Y/%m/%#d %H:%M:%S')))

            # CPU Info
            info.append(('CPU', "Physical cores", f'{psutil.cpu_count(logical=False)}'))
            info.append(('CPU', "Total cores", f'{psutil.cpu_count(logical=True)}'))
            # CPU frequencies
            cpufreq = psutil.cpu_freq()
            info.append(('CPU', "Max Frequency", f'{cpufreq.max:.2f}Mhz'))
            info.append(('CPU', "Min Frequency", f'{cpufreq.min:.2f}Mhz'))
            info.append(('CPU', "Current Frequency", f'{cpufreq.current:.2f}Mhz'))
            # CPU usage
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
                info.append(('CPU', f'Core {i}', f'{percentage}%'))
            info.append(('CPU', "Total CPU Usage", f'{psutil.cpu_percent()}%'))

            # Memory Information

            # get the memory details
            svmem = psutil.virtual_memory()
            info.append(('memory', "Memory Total",  f'{self.get_size(svmem.total)}'))
            info.append(('memory', "Memory Available",  f'{self.get_size(svmem.available)}'))
            info.append(('memory', "Memory Used",  f'{self.get_size(svmem.used)}'))
            info.append(('Memory', "Memory Percentage",  f'{svmem.percent}%'))
  
            # get the swap Memory details (if exists)
            swap = psutil.swap_memory()
            info.append(('Memory', "Swap Total",  f'{self.get_size(swap.total)}'))
            info.append(('Memory', "Swap Free", f'{self.get_size(swap.free)}'))
            info.append(('Memory', "Swap Used",  f'{self.get_size(swap.used)}'))
            info.append(('Memory', "Swap Percentage",  f'{swap.percent}%'))

            # disk information
            partitions = psutil.disk_partitions()
            for partition in partitions:
                info.append(('Disks', "Device",  partition.device))
                info.append(('Disks', "Mountpoint",  partition.mountpoint))
                info.append(('Disks', "File System Type",  partition.fstype))
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                except PermissionError: 
                    # this can be catched due to the disk that
                    # isn't ready
                    continue
                info.append(('Disks', "Total Size",  f'{self.get_size(partition_usage.total)}'))
                info.append(('Disks', "Used",  f'{self.get_size(partition_usage.used)}'))
                info.append(('Disks', "Free",  f'{self.get_size(partition_usage.free)}'))
                info.append(('Disks', "Percentage",  f'{partition_usage.percent}%'))
            # get IO statistics since boot
            disk_io = psutil.disk_io_counters()
            info.append(('Disks', "Total Read",  f'{self.get_size(disk_io.read_bytes)}'))
            info.append(('Disks', "Total Write",  f'{self.get_size(disk_io.write_bytes)}'))

            # network info
            if_addrs = psutil.net_if_addrs()
            for interface_name, interface_addresses in if_addrs.items():
                for address in interface_addresses:
                    if str(address.family) == 'AddressFamily.AF_INET':
                        info.append(('Network', f'{interface_name} IP Address',  address.address))
                        info.append(('Network', f'{interface_name} Netmask',  address.netmask))
                        info.append(('Network', f'{interface_name} Broadcast IP',  address.broadcast))
                    elif str(address.family) == 'AddressFamily.AF_PACKET': 
                        info.append(('Network', f'{interface_name} MAC Address',  address.address))
                        info.append(('Network', f'{interface_name} Netmask',  address.netmask))
                        info.append(('Network', f'{interface_name} Broadcast MAC',  address.broadcast))
            # get IO statistics since boot
            net_io = psutil.net_io_counters()
            info.append(('Network', 'Total Bytes Sent',  self.get_size(net_io.bytes_sent)))
            info.append(('Network', 'Total Bytes Received',  self.get_size(net_io.bytes_recv)))

            # process info
            if self.processes:
                for proc in psutil.process_iter():
                    with proc.oneshot():
                        # System Idle Process for Windows NT, useless to see anyways
                        if proc.pid == 0: 
                            continue
                        mem_info = proc.memory_info()
                        info.append(('Processes', f'{proc.name()}', f'PID : {proc.pid}, Status : {proc.status()}' \
                            f', Mem Usage : {self.get_size(mem_info.rss)}' \
                            f', Threads: {proc.num_threads()}'))

            # services
            if self.services:
                for service in psutil.win_service_iter():
                    info.append(('Services', service.name(), f'Username : {service.username()}' \
                        f', binpath : {service.binpath()}, Start Type : {service.start_type()}' \
                        f', Status : {service.status()}'))

            # envornment
            if self.environ:
                for k,v in os.environ.items():
                    info.append(('Environment', k, v))

        except Exception as e:
            info.append(('Error', 'error', str(e)))
        return info

    def build_record_info_out(self):
        """
        A non-interface helper for pi_push_all_records() responsible for creating the outgoing record layout.
        :param file_reader: The name for csv file reader.
        :return: The outgoing record layout, otherwise nothing.
        """

        record_info_out = Sdk.RecordInfo(self.alteryx_engine)  # A fresh record info object for outgoing records.
        #We are returning a single column and a single row. 
        
        record_info_out.add_field('category', Sdk.FieldType.string, 100)
        record_info_out.add_field('system property', Sdk.FieldType.string, 100)
        record_info_out.add_field('value', Sdk.FieldType.string, 1000)
        return record_info_out

    def pi_push_all_records(self, n_record_limit: int) -> bool:
        record_info_out = self.build_record_info_out()  # Building out the outgoing record layout.
        self.output_anchor.init(record_info_out)  # Lets the downstream tools know of the outgoing record metadata.
        record_creator = record_info_out.construct_record_creator()  # Creating a new record_creator for the new data.

        output_data = self.getSystemInfo()

        for category, name, value in output_data:
            record_info_out[0].set_from_string(record_creator, category)
            record_info_out[1].set_from_string(record_creator, name)
            record_info_out[2].set_from_string(record_creator, value)

            out_record = record_creator.finalize_record()
            self.output_anchor.push_record(out_record, False)  # False: completed connections will automatically close.
            record_creator.reset()  # Resets the variable length data to 0 bytes (default) to prevent unexpected results.


        self.display_info(f'Pushed {len(output_data)} records')
        self.output_anchor.close()  # Close outgoing connections.
        return True

    def pi_close(self, b_has_errors: bool):
        self.output_anchor.assert_close()  # Checks whether connections were properly closed.

    def display_error_msg(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, msg_string)

    def display_info(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.info, msg_string)


class IncomingInterface:
    def __init__(self, parent: AyxPlugin):
        pass

    def ii_init(self, record_info_in: Sdk.RecordInfo) -> bool:
        pass

   
    def ii_push_record(self, in_record: Sdk.RecordRef) -> bool:
        pass

    def ii_update_progress(self, d_percent: float):
        # Inform the Alteryx engine of the tool's progress.
        pass


    def ii_close(self):
        pass
