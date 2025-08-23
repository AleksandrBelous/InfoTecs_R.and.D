# -*- mode: ruby -*-
# vi: set ft=ruby :

# IPv4 Chat - DevOps окружение для тестирования

Vagrant.configure("2") do |config|
  # Полностью отключить vbguest
  # config.vbguest.auto_update = false   # не проверять версии
  # config.vbguest.no_install  = true    # и вовсе не пытаться устанавливать
  
  # VM definitions
  vms = {
    'debian' => { box: 'debian/bookworm64',    memory: 2048, cpus: 2 },
    'ubuntu' => { box: 'ubuntu/jammy64',       memory: 2048, cpus: 2 },
    'centos' => { box: 'centos/stream9',       memory: 2048, cpus: 2 }
  }
  
  # Configure each VM
  vms.each_with_index do |(name, vm_config), index|
    config.vm.define name do |node|
      node.vm.box = vm_config[:box]
      node.vm.hostname = name
      
      # Network configuration - use higher port range to avoid conflicts
      node.vm.network "forwarded_port", guest: 22, host: 2300 + index, auto_correct: false, id: "ssh"
      node.vm.network "forwarded_port", guest: 12345, host: 12345 + index, auto_correct: false
      
      # Internal network for inter-VM communication (broadcast support)
      node.vm.network "private_network", ip: "192.168.56.#{10 + index}", virtualbox__intnet: "ipv4chat"
      
      # VirtualBox settings
      node.vm.provider "virtualbox" do |vb|
        vb.name = "IPv4Chat-#{name.capitalize}"
        vb.memory = vm_config[:memory]
        vb.cpus = vm_config[:cpus]
        vb.gui = false
        vb.linked_clone = true
        
        # VBoxManage optimizations
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
        vb.customize ["modifyvm", :id, "--audio", "none"]
        vb.customize ["modifyvm", :id, "--usb", "off"]
        vb.customize ["modifyvm", :id, "--groups", "/IPv4Chat"]
      end
      
      # VM-specific setup provisioning
      case name
      when 'debian'
        node.vm.provision "ansible" do |ansible|
          ansible.playbook = "ansible/playbooks/vm-specific/debian-setup.yaml"
          ansible.inventory_path = "ansible/inventory.ini"
          ansible.config_file = "ansible/ansible.cfg"
          ansible.limit = "debian"
          ansible.become = true
        end
      when 'ubuntu'
        node.vm.provision "ansible" do |ansible|
          ansible.playbook = "ansible/playbooks/vm-specific/ubuntu-setup.yaml"
          ansible.inventory_path = "ansible/inventory.ini"
          ansible.config_file = "ansible/ansible.cfg"
          ansible.limit = "ubuntu"
          ansible.become = true
        end
      when 'centos'
        node.vm.provision "ansible" do |ansible|
          ansible.playbook = "ansible/playbooks/vm-specific/centos-setup.yaml"
          ansible.inventory_path = "ansible/inventory.ini"
          ansible.config_file = "ansible/ansible.cfg"
          ansible.limit = "redhat"
          ansible.become = true
        end
      end
      
      # IPv4 Chat application deployment after all VMs are up
      if name == vms.keys.last
        node.vm.provision "ansible" do |ansible|
          ansible.playbook = "ansible/playbooks/deploy.yaml"
          ansible.inventory_path = "ansible/inventory.ini"
          ansible.config_file = "ansible/ansible.cfg"
          ansible.limit = "all"
          ansible.become = true
        end
      end
    end
  end
end
