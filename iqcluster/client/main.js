import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { mcJobs } from '../both/collections.js';
import { nodeStats } from '../both/collections.js';

import './main.html';

Template.hello.onCreated(function helloOnCreated() {
  // counter starts at 0
  this.counter = new ReactiveVar(0);
});

Template.hello.helpers({
  counter() {
    return Template.instance().counter.get();
  },
});

Template.clusterstats.helpers({
  stats() {
    return nodeStats.find();
    return [
      {"node" : "master", "cpu_usage": "2"},
      {"node" : "node001", "cpu_usage": "1"},
      {"node" : "node002", "cpu_usage": "14"},
      {"node" : "node003", "cpu_usage": "0"}
    ] 
  }
})

Template.body.events({
  'submit .newJobForm'(event) {
    event.preventDefault();
    const target = event.target;
    const cmd = target.command.value;
    const np = target.numprocs.value;
    const ms = target.master.checked;
    const n1 = target.node001.checked;
    const n2 = target.node002.checked;
    const n3 = target.node003.checked;
    const q = target.queue.value;
    const userId = Meteor.userId();

    target.command.value = ""
    target.numprocs.value = ""
    target.master.checked = false
    target.node001.checked = false
    target.node002.checked = false
    target.node003.checked = false
    target.queue.value = ""
    console.log('cmd: ',cmd);
    console.log('np: ',np);
    console.log('ms: ',ms);
    console.log('n1: ',n1);
    console.log('n2: ',n2);
    console.log('n3: ',n3);
    console.log('q: ',q);
    console.log('userId: ',userId);
    console.log('----')
    master_status = '';
    node001_status = '';
    node002_status = '';
    node003_status = '';
    if(!ms) master_status = 'pending'; else master_status = 'excluded'
    if(!n1) node001_status = 'pending'; else node001_status = 'excluded'
    if(!n2) node002_status = 'pending'; else node002_status = 'excluded'
    if(!n3) node003_status = 'pending'; else node003_status = 'excluded'
    mcJobs.insert({
      userId: userId,
      createdAt: new Date(),
      cmd: cmd,
      numprocs: np,
      queue: q,
      scheduled: 'no',
      master_status: master_status,
      node001_status: node001_status,
      node002_status: node002_status,
      node003_status: node003_status
    })
  }
})

Template.body.helpers({
  jobs() {
    return mcJobs.find({userId: Meteor.userId()}, {sort : { createdAt: -1 }});
  }
})

Template.hello.events({
  'click button'(event, instance) {
    // increment the counter when button is clicked
    instance.counter.set(instance.counter.get() + 1);
  },
});

Accounts.ui.config({
  passwordSignupFields: "USERNAME_ONLY"
})
