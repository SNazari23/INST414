import yfinance as yf
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy
from collections import defaultdict, deque
import random
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

class SpecificInvestmentFirmTree:
    def __init__(self):
        self.graph = nx.Graph()
        self.firms = [
            'Fidelity', 'Charles Schwab', 'BlackRock', 'Blackstone', 
            'Morgan Stanley', 'J.P. Morgan', 'Goldman Sachs', 
            'Vanguard', 'UBS', 'T. Rowe Price'
        ]
        self.stock_data = {}
        
    def get_popular_stocks(self):
        """Get a comprehensive list of major stocks"""
        major_stocks = [
            # Technology
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AVGO', 'ORCL',
            'ADBE', 'CRM', 'CSCO', 'INTC', 'AMD', 'QCOM', 'TXN', 'IBM', 'NOW',
            
            # Financial Services
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'SCHW', 'BLK', 'AXP', 'V', 
            'MA', 'PYPL', 'SQ', 'DFS', 'COF', 'USB', 'PNC',
            
            # Healthcare
            'JNJ', 'PFE', 'MRK', 'ABT', 'TMO', 'DHR', 'LLY', 'UNH', 'CVS',
            'GILD', 'AMGN', 'BIIB', 'REGN', 'VRTX', 'MRNA',
            
            # Consumer
            'PG', 'KO', 'PEP', 'WMT', 'TGT', 'COST', 'HD', 'LOW', 'NKE', 'MCD',
            'SBUX', 'DIS', 'NFLX', 'CMCSA', 'T', 'VZ', 'TMUS',
            
            # Industrial & Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'BA', 'LMT', 'RTX', 'HON', 'CAT',
            'DE', 'GE', 'MMM',
        ]
        return major_stocks
    
    def get_firm_investment_style(self, firm):
        """Define investment style for each firm"""
        styles = {
            'Fidelity': {'type': 'active_equity', 'concentration': 'medium', 'sector_bias': 'growth'},
            'Charles Schwab': {'type': 'index_passive', 'concentration': 'high', 'sector_bias': 'broad_market'},
            'BlackRock': {'type': 'index_passive', 'concentration': 'high', 'sector_bias': 'broad_market'},
            'Blackstone': {'type': 'private_equity', 'concentration': 'high', 'sector_bias': 'value'},
            'Morgan Stanley': {'type': 'investment_bank', 'concentration': 'medium', 'sector_bias': 'financials'},
            'J.P. Morgan': {'type': 'investment_bank', 'concentration': 'medium', 'sector_bias': 'financials'},
            'Goldman Sachs': {'type': 'investment_bank', 'concentration': 'medium', 'sector_bias': 'financials'},
            'Vanguard': {'type': 'index_passive', 'concentration': 'high', 'sector_bias': 'broad_market'},
            'UBS': {'type': 'wealth_management', 'concentration': 'medium', 'sector_bias': 'conservative'},
            'T. Rowe Price': {'type': 'active_equity', 'concentration': 'medium', 'sector_bias': 'growth'}
        }
        return styles.get(firm, {'type': 'general', 'concentration': 'medium', 'sector_bias': 'broad_market'})
    
    def simulate_firm_holdings(self, firm, stocks):
        """Simulate realistic stock holdings based on firm's investment style"""
        style = self.get_firm_investment_style(firm)
        holdings = {}
        
        # Base number of holdings based on firm type
        if style['type'] in ['index_passive', 'wealth_management']:
            num_holdings = random.randint(80, 150)  # Broad diversification
        elif style['type'] == 'active_equity':
            num_holdings = random.randint(40, 80)   # Focused portfolio
        else:  # investment_bank, private_equity
            num_holdings = random.randint(20, 50)   # Concentrated positions
        
        # Ensure we don't request more stocks than available
        num_holdings = min(num_holdings, len(stocks))
        
        # Select stocks based on investment style
        if style['sector_bias'] == 'financials':
            # Heavy on financial stocks
            financial_stocks = [s for s in stocks if s in ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'SCHW', 'BLK', 'AXP', 'V', 'MA']]
            other_stocks = [s for s in stocks if s not in financial_stocks]
            selected_stocks = financial_stocks + random.sample(other_stocks, min(len(other_stocks), max(5, num_holdings - len(financial_stocks))))
        elif style['sector_bias'] == 'growth':
            # Growth-oriented stocks (tech, consumer discretionary)
            growth_stocks = [s for s in stocks if s in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'ADBE', 'CRM', 'NFLX', 'DIS']]
            other_stocks = [s for s in stocks if s not in growth_stocks]
            selected_stocks = growth_stocks + random.sample(other_stocks, min(len(other_stocks), max(10, num_holdings - len(growth_stocks))))
        elif style['sector_bias'] == 'value':
            # Value stocks (energy, industrials, some financials)
            value_stocks = [s for s in stocks if s in ['XOM', 'CVX', 'JPM', 'BAC', 'JNJ', 'PG', 'KO', 'WMT']]
            other_stocks = [s for s in stocks if s not in value_stocks]
            selected_stocks = value_stocks + random.sample(other_stocks, min(len(other_stocks), max(10, num_holdings - len(value_stocks))))
        else:  # broad_market, conservative
            selected_stocks = random.sample(stocks, num_holdings)
        
        # Remove duplicates and ensure we have the right number
        selected_stocks = list(set(selected_stocks))[:num_holdings]
        
        # Assign weights based on concentration
        if style['concentration'] == 'high':
            weights = np.random.dirichlet(np.ones(len(selected_stocks)) * 0.5) * 100
        elif style['concentration'] == 'medium':
            weights = np.random.dirichlet(np.ones(len(selected_stocks)) * 1.0) * 100
        else:
            weights = np.random.dirichlet(np.ones(len(selected_stocks)) * 2.0) * 100
        
        # Normalize weights to sum to 100
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w * 100 / total_weight for w in weights]
        
        # Create holdings dictionary
        for stock, weight in zip(selected_stocks, weights):
            if weight > 0.1:  # Only include holdings > 0.1%
                holdings[stock] = round(weight, 2)
        
        return holdings
    
    def build_firm_tree(self):
        """Build the investment firm stock relationship tree with specified firms"""
        stocks = self.get_popular_stocks()
        
        print("Building investment firm stock relationship tree...")
        
        # Create binary tree structure with firms as nodes
        # Using a hierarchical structure based on firm types
        firm_types = {
            'asset_managers': ['BlackRock', 'Vanguard', 'Fidelity', 'T. Rowe Price'],
            'investment_banks': ['Morgan Stanley', 'J.P. Morgan', 'Goldman Sachs'],
            'wealth_management': ['Charles Schwab', 'UBS'],
            'alternative_managers': ['Blackstone']
        }
        
        # Add all firm nodes
        for firm in self.firms:
            self.graph.add_node(firm, type='firm', size=2000)
        
        # Create edges between firms (peer relationships)
        # Connect firms within same categories
        for category, firms_in_category in firm_types.items():
            for i in range(len(firms_in_category)):
                for j in range(i + 1, len(firms_in_category)):
                    if firms_in_category[i] in self.firms and firms_in_category[j] in self.firms:
                        self.graph.add_edge(firms_in_category[i], firms_in_category[j], 
                                          relationship='same_category', weight=2)
        
        # Connect major players across categories
        cross_category_connections = [
            ('BlackRock', 'J.P. Morgan'), ('Vanguard', 'Morgan Stanley'),
            ('Fidelity', 'Goldman Sachs'), ('Blackstone', 'Goldman Sachs'),
            ('Charles Schwab', 'Fidelity'), ('UBS', 'Morgan Stanley')
        ]
        
        for firm1, firm2 in cross_category_connections:
            if firm1 in self.firms and firm2 in self.firms:
                self.graph.add_edge(firm1, firm2, relationship='strategic_partner', weight=1)
        
        # Add stock holdings as edges
        for firm in self.firms:
            print(f"Processing holdings for {firm}...")
            holdings = self.simulate_firm_holdings(firm, stocks)
            
            for stock, weight in holdings.items():
                # Add stock node if not exists
                if stock not in self.graph:
                    self.graph.add_node(stock, type='stock', size=800)
                
                # Add edge between firm and stock
                self.graph.add_edge(firm, stock, weight=weight, 
                                  relationship=f'holds_{weight}%')
    
    def visualize_tree(self):
        """Visualize the investment firm stock relationship tree"""
        if len(self.graph.nodes()) == 0:
            print("No graph data to visualize. Please build the tree first.")
            return
            
        plt.figure(figsize=(20, 15))
        
        # Create a hierarchical layout
        pos = self._create_custom_layout()
        
        # Separate nodes by type
        firm_nodes = [node for node in self.graph.nodes() if self.graph.nodes[node].get('type') == 'firm']
        stock_nodes = [node for node in self.graph.nodes() if self.graph.nodes[node].get('type') == 'stock']
        
        # Draw firms (larger rectangles)
        if firm_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=firm_nodes,
                                  node_color='lightblue', node_shape='s',
                                  node_size=3000, alpha=0.9,
                                  edgecolors='darkblue', linewidths=3)
        
        # Draw stocks (smaller circles)
        if stock_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=stock_nodes,
                                  node_color='lightgreen', node_shape='o',
                                  node_size=1000, alpha=0.7,
                                  edgecolors='darkgreen', linewidths=2)
        
        # Separate edges by type
        firm_edges = [(u, v) for u, v, attr in self.graph.edges(data=True) 
                      if attr.get('relationship') in ['same_category', 'strategic_partner']]
        stock_edges = [(u, v) for u, v, attr in self.graph.edges(data=True) 
                       if 'holds' in attr.get('relationship', '')]
        
        # Draw firm-to-firm edges
        if firm_edges:
            nx.draw_networkx_edges(self.graph, pos, edgelist=firm_edges,
                                  edge_color='blue', width=2, alpha=0.6,
                                  style='dashed')
        
        # Draw firm-to-stock edges with weights
        if stock_edges:
            stock_edge_weights = [self.graph[u][v].get('weight', 1) for u, v in stock_edges]
            nx.draw_networkx_edges(self.graph, pos, edgelist=stock_edges,
                                  edge_color='red', width=[min(w/20, 5) for w in stock_edge_weights],  # Cap width at 5
                                  alpha=0.4, style='solid')
        
        # Add edge labels for significant stock holdings (>2%)
        significant_edges = [(u, v) for u, v, attr in self.graph.edges(data=True) 
                           if 'holds' in attr.get('relationship', '') and attr.get('weight', 0) > 2]
        
        significant_edge_labels = {(u, v): f"{attr['weight']}%" 
                                 for u, v, attr in self.graph.edges(data=True) 
                                 if 'holds' in attr.get('relationship', '') and attr.get('weight', 0) > 2}
        
        if significant_edge_labels:
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=significant_edge_labels,
                                       font_color='red', font_size=7)
        
        # Add node labels
        labels = {node: node for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, font_weight='bold')
        
        plt.title("What are the relations between investment firms stocks?", fontsize=14, pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def _create_custom_layout(self):
        """Create a custom layout that positions firms centrally and stocks around them"""
        pos = {}
        
        # Position firms in a circle
        firms = [node for node in self.graph.nodes() if self.graph.nodes[node].get('type') == 'firm']
        stocks = [node for node in self.graph.nodes() if self.graph.nodes[node].get('type') == 'stock']
        
        if not firms and not stocks:
            return pos
            
        # Place firms in a circle
        radius = 3
        angle_step = 2 * np.pi / max(1, len(firms))
        
        for i, firm in enumerate(firms):
            angle = i * angle_step
            pos[firm] = (radius * np.cos(angle), radius * np.sin(angle))
        
        # Place stocks in concentric circles around connected firms
        for stock in stocks:
            connected_firms = [n for n in self.graph.neighbors(stock) if self.graph.nodes[n].get('type') == 'firm']
            if connected_firms:
                # Position stock near its primary holder (largest weight)
                primary_firm = max(connected_firms, 
                                 key=lambda firm: self.graph[firm][stock].get('weight', 0) if self.graph.has_edge(firm, stock) else 0)
                
                if primary_firm in pos:
                    # Add some random offset
                    angle_offset = random.uniform(0, 2 * np.pi)
                    distance = random.uniform(0.5, 1.5)
                    x = pos[primary_firm][0] + distance * np.cos(angle_offset)
                    y = pos[primary_firm][1] + distance * np.sin(angle_offset)
                    pos[stock] = (x, y)
                else:
                    # Random position if primary firm not in pos (shouldn't happen)
                    pos[stock] = (random.uniform(-4, 4), random.uniform(-4, 4))
            else:
                # Random position for unconnected stocks
                pos[stock] = (random.uniform(-4, 4), random.uniform(-4, 4))
        
        return pos
    
    def analyze_holdings(self):
        """Analyze and display holdings information"""
        print("\n" + "="*60)
        print("INVESTMENT FIRM STOCK HOLDINGS ANALYSIS")
        print("="*60)
        
        # Analyze each firm's portfolio
        for firm in self.firms:
            print(f"\n {firm} Portfolio Analysis:")
            holdings = []
            if firm in self.graph:
                holdings = [(stock, self.graph[firm][stock]['weight']) 
                           for stock in self.graph.neighbors(firm) 
                           if self.graph.nodes[stock].get('type') == 'stock' and self.graph.has_edge(firm, stock)]
            
            # Sort by weight descending
            holdings.sort(key=lambda x: x[1], reverse=True)
            
            print(f"   Total stocks held: {len(holdings)}")
            if holdings:
                print(f"   Top 5 holdings:")
                for stock, weight in holdings[:5]:
                    print(f"     {stock}: {weight}%")
                
                # Calculate concentration (Herfindahl index)
                total_weight = sum(weight for _, weight in holdings)
                if total_weight > 0:
                    concentration = sum((weight/total_weight)**2 for _, weight in holdings)
                    print(f"   Portfolio concentration: {concentration:.3f}")
            else:
                print(f"   No stock holdings found")
        
        # Find commonly held stocks
        print(f"\n Most Commonly Held Stocks Across All Firms:")
        stock_holders = defaultdict(list)
        for firm in self.firms:
            if firm in self.graph:
                for stock in self.graph.neighbors(firm):
                    if self.graph.nodes[stock].get('type') == 'stock' and self.graph.has_edge(firm, stock):
                        weight = self.graph[firm][stock].get('weight', 0)
                        stock_holders[stock].append((firm, weight))
        
        # Sort by number of holders and show top 10
        sorted_stocks = sorted(stock_holders.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for stock, holders in sorted_stocks:
            print(f"   {stock}: Held by {len(holders)} firms")
            if holders:
                top_holder = max(holders, key=lambda x: x[1])
                print(f"     Largest holder: {top_holder[0]} ({top_holder[1]}%)")
        
        # Show firm relationships
        print(f"\n Firm Relationships:")
        for firm1, firm2, data in self.graph.edges(data=True):
            if (self.graph.nodes[firm1].get('type') == 'firm' and 
                self.graph.nodes[firm2].get('type') == 'firm'):
                rel_type = data.get('relationship', 'connection')
                print(f"   {firm1} ↔ {firm2} ({rel_type})")

# Create and run the specific firm tree
def main():
    firm_tree = SpecificInvestmentFirmTree()
    firm_tree.build_firm_tree()
    firm_tree.visualize_tree()
    firm_tree.analyze_holdings()
    
    # Print summary statistics
    print(f"\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total firms: {len(firm_tree.firms)}")
    stock_count = len([n for n in firm_tree.graph.nodes() if firm_tree.graph.nodes[n].get('type') == 'stock'])
    print(f"Total stocks in network: {stock_count}")
    print(f"Total relationships: {firm_tree.graph.number_of_edges()}")

if __name__ == "__main__":
    main()