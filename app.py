from flask import Flask, jsonify, request, render_template, redirect, url_for
import json
import hashlib
from datetime import datetime
import os

app = Flask(__name__)

FILE_NAME = 'blockchain.json'

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the first block of the blockchain"""
        if not os.path.exists(FILE_NAME):
            genesis_block = {
                'index': 0,
                'timestamp': str(datetime.now()),
                'data': 'Genesis Block',
                'previous_hash': '0',
                'hash': self.calculate_hash(0, str(datetime.now()), 'Genesis Block', '0')
            }
            self.chain.append(genesis_block)
            self.save_blockchain()

    def create_block(self, data):
        """Creates a new block and adds it to the blockchain"""
        previous_block = self.get_last_block()
        index = len(self.chain)
        timestamp = str(datetime.now())
        previous_hash = previous_block['hash']
        block_hash = self.calculate_hash(index, timestamp, data, previous_hash)

        block = {
            'index': index,
            'timestamp': timestamp,
            'data': data,
            'previous_hash': previous_hash,
            'hash': block_hash
        }

        self.chain.append(block)
        self.save_blockchain()

    def calculate_hash(self, index, timestamp, data, previous_hash):
        """Calculates the hash of a block"""
        block_string = f'{index}{timestamp}{data}{previous_hash}'
        return hashlib.sha256(block_string.encode()).hexdigest()

    def get_last_block(self):
        """Returns the last block in the chain"""
        return self.chain[-1]

    def is_chain_valid(self):
        """Checks the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block['hash'] != self.calculate_hash(
                current_block['index'], current_block['timestamp'],
                current_block['data'], current_block['previous_hash']
            ):
                return False

            if current_block['previous_hash'] != previous_block['hash']:
                return False

        return True

    def save_blockchain(self):
        """Saves the blockchain to a file"""
        with open(FILE_NAME, 'w') as f:
            json.dump(self.chain, f, indent=4)

    def load_blockchain(self):
        """Loads the blockchain from a file"""
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'r') as f:
                self.chain = json.load(f)

blockchain = Blockchain()
blockchain.load_blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    drug_id = request.form['drug_id']
    action = request.form['action']
    manufacturer = request.form['manufacturer']

    if not drug_id or not action or not manufacturer:
        return jsonify({'error': 'Missing required fields'}), 400

    transaction_data = {
        'drug_id': drug_id,
        'action': action,
        'manufacturer': manufacturer
    }

    blockchain.create_block(transaction_data)
    return redirect(url_for('index'))

@app.route('/view_transactions')
def view_transactions():
    return render_template('transactions.html', transactions=blockchain.chain)

@app.route('/verify_transactions')
def verify_transactions():
    valid = blockchain.is_chain_valid()
    message = 'All transactions are valid' if valid else 'Blockchain integrity check failed!'
    return render_template('verify.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
