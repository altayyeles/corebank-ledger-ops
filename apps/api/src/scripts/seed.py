
from decimal import Decimal
from sqlalchemy.orm import Session

from src.core.db import SessionLocal
from src.core.utils import uid, gen_iban
from src.core.security import hash_password

from src.identity.models import User, Role
from src.customer.models import Customer, KycProfile
from src.accounts.models import Product, Account, AccountBalance, Limit
from src.ledger.service import ensure_core_coa, post_entry, apply_balance_projection_from_entry
from src.ledger.models import CoaAccount
from src.fraud.service import ensure_default_rules


def main():
    db: Session = SessionLocal()
    try:
        def ensure_role(name: str):
            r = db.query(Role).filter(Role.name == name).first()
            if not r:
                r = Role(id=uid(), name=name)
                db.add(r)
            return r

        admin_role = ensure_role('admin')
        teller_role = ensure_role('teller')
        customer_role = ensure_role('customer')
        db.commit()

        def ensure_user(email: str, password: str, roles: list[Role]):
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(id=uid(), email=email, password_hash=hash_password(password))
                u.roles = roles
                db.add(u)
                db.commit()
            return u

        ensure_user('admin@demo.local', 'Admin123!', [admin_role])
        cust_user = ensure_user('customer@demo.local', 'Customer123!', [customer_role])

        cust = db.query(Customer).filter(Customer.email == 'customer@demo.local').first()
        if not cust:
            cust = Customer(id=uid(), full_name='Demo Customer', email='customer@demo.local', phone='+90-000-000-0000')
            db.add(cust)
            db.add(KycProfile(customer_id=cust.id, level='VERIFIED'))
            db.commit()

        cust_user.customer_id = cust.id
        db.commit()

        dda = db.query(Product).filter(Product.code == 'DDA_TRY').first()
        if not dda:
            dda = Product(id=uid(), code='DDA_TRY', name='Vadesiz TRY', type='DDA', currency='TRY')
            db.add(dda)
            db.commit()

        accs = db.query(Account).filter(Account.customer_id == cust.id).all()
        if len(accs) < 2:
            acc_a = Account(id=uid(), customer_id=cust.id, product_id=dda.id, iban=gen_iban())
            acc_b = Account(id=uid(), customer_id=cust.id, product_id=dda.id, iban=gen_iban())
            db.add(acc_a); db.add(acc_b)
            db.add(AccountBalance(account_id=acc_a.id, ledger_balance=Decimal('0'), available_balance=Decimal('0')))
            db.add(AccountBalance(account_id=acc_b.id, ledger_balance=Decimal('0'), available_balance=Decimal('0')))
            db.add(Limit(id=uid(), account_id=acc_a.id, daily_out_limit=Decimal('50000'), per_tx_limit=Decimal('20000')))
            db.commit()
        else:
            acc_a, acc_b = accs[0], accs[1]

        ensure_core_coa(db)
        coa_cash = db.query(CoaAccount).filter(CoaAccount.code == '101.01').first()
        coa_dep = db.query(CoaAccount).filter(CoaAccount.code == '201.01').first()

        from src.ledger.models import JournalEntry
        if not db.query(JournalEntry).filter(JournalEntry.business_tx_id == 'SEED-FUND').first():
            je = post_entry(db, 'SEED-FUND', 'Initial funding', 'TRY', [
                {"coa_account_id": coa_cash.id, "debit": Decimal('10000.00'), "credit": Decimal('0')},
                {"coa_account_id": coa_dep.id, "debit": Decimal('0'), "credit": Decimal('10000.00'), "account_id": acc_a.id},
            ])
            apply_balance_projection_from_entry(db, je)

        ensure_default_rules(db)

        print('Seed completed.')
        print('Demo customer id:', cust.id)
        print('Account A:', acc_a.id, acc_a.iban)
        print('Account B:', acc_b.id, acc_b.iban)
    finally:
        db.close()


if __name__ == '__main__':
    main()
