import os
from flask import Flask, render_template, Response, redirect, url_for, request
from datetime import datetime
import modules.database as db


ticket = db.query_ticket(1)

print(ticket.priority.name)
print(dir(ticket.priority))